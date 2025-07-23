from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, func, or_
from Config.dbConnection import engine 
from Models.shared import customerRegistration, customerUserProfile
from Schemas.shared import StatusResult, SystemLogErrorSchema, SystemActivitySchema, RegistrationViewModelSchema, CustomerOtpSchema, CBSCustomerFullInfoSchema, CustomerUserProfileSchema
from Services.GenericCRUDServices import GenericInserter
from Services.LogServices import AddLogOrError
from Services.ActivityServices import AddActivityLog
from Services.AppSettingsServices import FetchAppSettingsByKey
from Services.CommonServices import ConvertToBool, GetSha1Hash, GetEncryptedText, SendCredentials, SendSMS, SendEmail, GetErrorMessage
from Services.CBSServices import GetCustomerFullInformation
from Services.OTPServices import GenerateCode, Authentication

RegistrationRoutes = APIRouter(prefix="/Registration")

@RegistrationRoutes.get("/IsUserIDAvailable")
def IsUserIDAvailable(user_id: str) -> StatusResult:
    status = StatusResult()
    try:
        user_profile = CustomerUserProfileSchema()
        
        with engine.connect() as _conn:
            result = _conn.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == user_id.lower())).first()
        
            if result:
                user_profile = CustomerUserProfileSchema(**dict(result._mapping))
            else:
                user_profile = None
        
        status.Status = "OK"
        status.Message = None
        status.Result = not bool(user_profile)
        
        return status
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        return status

@RegistrationRoutes.post("/SignUp")
async def SignUp(data:RegistrationViewModelSchema) -> StatusResult:
    status = StatusResult[object]()
    try:
        # UserID Setting
        if not ConvertToBool(FetchAppSettingsByKey("AUTO_SET_USER_ID_AT_SIGNUP")):
            if not data.user_id:
                status.Status = "FAILED"
                status.Message = "User ID is required."
                status.Result = None
                return status
        else:
            user_id_type = FetchAppSettingsByKey("AUTO_SET_USER_ID_TYPE_AT_SIGNUP").upper()
            
            if user_id_type == "CIF":
                data.user_id = data.customer_id
            elif user_id_type == "CIF_NON_ZERO":
                data.user_id = data.customer_id.lstrip("0")
            elif user_id_type == "MOBILE":
                data.user_id = data.phone_number
            elif user_id_type == "MOBILE_CIF":
                data.user_id = data.phone_number + data.customer_id
            elif user_id_type == "MOBILE_CIF_NON_ZERO":
                data.user_id = data.phone_number + data.customer_id.lstrip("0")
        
        # Checking Existing Customer
        with engine.connect() as _conn:
            existing_user = _conn.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == data.user_id.lower())).first()
        
        if existing_user:
            status.Status = "FAILED"
            status.Message = "System does not allow same userid for multiple user."
            status.Result = ""
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        # Get CBS Data By CustomerID
        cbs_customer_full_info = GetCustomerFullInformation(data.customer_id)
        
        if not cbs_customer_full_info:
            status.Status = "FAILED"
            status.Message = "Invalid Customer ID."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
                
            return status
        
        # Checking Customer Type
        with engine.connect() as _conn:
            existing_user = _conn.execute(customerUserProfile.select().where(customerUserProfile.c.CUSTOMER_ID == data.customer_id)).first()
                
        if existing_user:
            status.Status = "FAILED"
            status.Message = "System does not allow multiple user for Individual type customer."
            status.Result = ""
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        if ConvertToBool(FetchAppSettingsByKey("RESTRICT_SAME_MOBILE_NO_AT_SIGNUP")):
            with engine.connect() as _conn:
                existing_users_same_mobile = _conn.execute(customerUserProfile.select().where(customerUserProfile.c.MOBILE_NUMBER_HASH == GetSha1Hash(data.phone_number))).first()
            
            if existing_users_same_mobile:
                status.Status = "FAILED"
                status.Message = "System does not allow same mobile number for multiple user."
                status.Result = ""
                
                AddActivityLog(SystemActivitySchema(
                    Type="SELF-SIGNUP",
                    Title="Failed to add a SignUp Request",
                    Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.user_id.lower()
                ))
                
                return status
        
        # Check Data with CBS
        # Customer ID Checking
        if data.customer_id != cbs_customer_full_info.customer.customer_id:
            status.Status = "FAILED"
            status.Message = "Invalid Customer ID."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
            
        
        # Birth Date Checking
        if not data.birth_date or data.birth_date.strftime("%d/%m/%Y") == "01/01/0001":
            status.Status = "FAILED"
            status.Message = "Date of Birth is required."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        if cbs_customer_full_info.customer.birth_date:
            if data.birth_date.strftime("%d-%b-%Y") != cbs_customer_full_info.customer.birth_date.strftime("%d-%b-%Y"):
                status.Status = "FAILED"
                status.Message = "Invalid Date of Birth."
                status.Result = None
                
                AddActivityLog(SystemActivitySchema(
                    Type="SELF-SIGNUP",
                    Title="Failed to add a SignUp Request",
                    Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.user_id.lower()
                ))
                
                return status
        else:
            status.Status = "FAILED"
            status.Message = "No Date of Birth found in CBS. Please contact with your branch for further details"
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        # TaxID Checking
        if not data.tax_id:
            status.Status = "FAILED"
            status.Message = "Tax ID is required."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        if cbs_customer_full_info.customer.tax_id:                
            if data.tax_id != cbs_customer_full_info.customer.tax_id:
                status.Status = "FAILED"
                status.Message = "Invalid Tax ID."
                status.Result = None
                
                AddActivityLog(SystemActivitySchema(
                    Type="SELF-SIGNUP",
                    Title="Failed to add a SignUp Request",
                    Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.user_id.lower()
                ))
                
                return status
        else:
            status.Status = "FAILED"
            status.Message = "No Tax ID information found in CBS. Please contact with your branch for further details"
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        # Email Checking
        if cbs_customer_full_info.emails:
            validEmail = False
            for item in cbs_customer_full_info.emails:
                if data.email and data.email.strip():
                    if data.email == item.address:
                        validEmail = True
                        break
            
            if data.email and data.email.strip() and not validEmail:
                status.Status = "FAILED"
                status.Message = "Invalid Email."
                status.Result = None
                
                AddActivityLog(SystemActivitySchema(
                    Type="SELF-SIGNUP",
                    Title="Failed to add a SignUp Request",
                    Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.user_id.lower()
                ))
                
                return status
                
        
        # Mobile No Checking
        if not data.phone_number:
            status.Status = "FAILED"
            status.Message = "Mobile Number is required."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        if cbs_customer_full_info.phones:
            validPhone = False
            for item in cbs_customer_full_info.phones:
                if data.phone_number == item.number:
                    validPhone = True
                    break
            
            if not validPhone:
                status.Status = "FAILED"
                status.Message = "Invalid Mobile Number."
                status.Result = None
                
                AddActivityLog(SystemActivitySchema(
                    Type="SELF-SIGNUP",
                    Title="Failed to add a SignUp Request",
                    Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.user_id.lower()
                ))
                
                return status
        else:
            status.Status = "FAILED"
            status.Message = "Update Mobile Number in CBS First."
            status.Result = None
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        # Send OTP & Check OTP
        status = await Authentication(CustomerOtpSchema(
            user_id=data.user_id.lower(),
            cust_id=data.customer_id,
            phone_number=data.phone_number,
            email_address=data.email,
            verification_channel=data.OTP_verify_channel,
            otp=data.OTP
        ))
        
        if  status.Status.upper() != "OK":
            return status
            
        # Check Previous SignUp Request
        with engine.connect() as _conn:
            previousSignUpRequests = _conn.execute(
                customerRegistration.select().where(
                    and_(
                        or_(
                            func.lower(customerRegistration.c.USER_ID) == data.user_id.lower(),
                            customerRegistration.c.CUSTOMER_ID == data.customer_id,
                            customerRegistration.c.TAX_ID == data.tax_id,
                            customerRegistration.c.PHONE_NUMBER == data.phone_number
                        ),
                        customerRegistration.c.STATUS == "PROCESSED"
                    )
                )
            ).fetchall()
        
        if previousSignUpRequests:
            status.Status = "FAILED"
            status.Message = "The provided credentials are already in use. Please contact with the administrator."
            status.Result = ""
            
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
            return status
        
        # Save SignUp Request
        insert_stmt = customerRegistration.insert().values(
                        BRANCH_ID=cbs_customer_full_info.customer.branch_code,
                        BRANCH_NM="",
                        USER_ID=data.user_id.lower(),
                        CUSTOMER_TTITLE=data.customer_title.upper(),
                        CUSTOMER_ID=data.customer_id,
                        TAX_ID=data.tax_id,
                        PHONE_NUMBER=data.phone_number,
                        EMAIL=data.email,
                        BIRTH_DATE=data.birth_date,
                        REMARK=data.remark,
                        CREATE_BY=data.user_id.lower(),
                        CREATE_DT=datetime.now(),
                        STATUS="PENDING"
                    )
        
        with engine.begin() as _conn:
            _conn.execute(insert_stmt)
        
        # Include User in CustomerUserProfile
        plain_password = GenerateCode()
        new_user_profile = CustomerUserProfileSchema(
            user_id=data.user_id.lower(),
            user_nm=cbs_customer_full_info.customer.name.upper(),
            user_descrip="Self Sign In",
            password_string=GetSha1Hash(plain_password),
            force_password_changed_flag=True,
            last_password_changed_on=datetime.now(),
            last_signed_on=None,
            user_status_active_flag=True,
            user_status_changed_on=datetime.now(),
            user_profile_closed_flag=False,
            user_profile_closed_on=None,
            failed_login_attempts_nos=0,
            failed_pasword_recovery_attempts_nos=0,
            failed_userid_recovery_attempts_nos=0,
            failed_tpin_recovery_attempts_nos=0,
            recent_alert_msg=None,
            customer_id=cbs_customer_full_info.customer.customer_id,
            home_branch_id=cbs_customer_full_info.customer.branch_code,
            user_address=", ".join(
                filter(None, [
                    cbs_customer_full_info.addresses[0].line_1,
                    cbs_customer_full_info.addresses[0].line_2,
                    cbs_customer_full_info.addresses[0].line_3,
                    cbs_customer_full_info.addresses[0].line_4,
                    cbs_customer_full_info.addresses[0].city,
                    cbs_customer_full_info.addresses[0].state_code
                ])
            ) + (f", Zipcode : {cbs_customer_full_info.addresses[0].zip_code}" 
                if cbs_customer_full_info.addresses[0].zip_code else ""),
            email_address=GetEncryptedText(data.email),
            email_address_hash=GetSha1Hash(data.email),
            mobile_number=GetEncryptedText(data.phone_number),
            mobile_number_hash=GetSha1Hash(data.phone_number),
            authentication_type=FetchAppSettingsByKey("DEFAULT_AUTHENTICATION_TYPE"),
            created_by=data.user_id.lower(),
            creation_dt=datetime.now(),
            last_activation_by=data.user_id.lower(),
            last_activation_dt=datetime.now(),
            auth_1st_by=None,
            auth_2nd_by=None,
            auth_1st_dt=None,
            auth_2nd_dt=None,
            auth_status_id="A",
            last_action="ADD",
            locked_flag=False,
            locked_by=None,
            locked_dt=None,
            locked_reason=None
        )

        GenericInserter[CustomerUserProfileSchema].insert_record(
            table=customerUserProfile,
            schema_model=CustomerUserProfileSchema,
            data=new_user_profile,
            returning_fields=[]
        )
        status = await SendCredentials(new_user_profile, "SIGNUP", plain_password)
        
        if status.Status == "OK":
            # Update SignUp Request to PROCESSED
            update_customerRegistration = customerRegistration.update().values(
                                STATUS="PROCESSED"
                            ).where(
                                and_(
                                    customerRegistration.c.BRANCH_ID == cbs_customer_full_info.customer.branch_code,
                                    customerRegistration.c.USER_ID == data.user_id.lower(),
                                    customerRegistration.c.CUSTOMER_ID == data.customer_id,
                                    customerRegistration.c.TAX_ID == data.tax_id,
                                    customerRegistration.c.PHONE_NUMBER == data.phone_number,
                                    customerRegistration.c.BIRTH_DATE == data.birth_date,
                                    customerRegistration.c.STATUS == "PENDING"
                                )
                            )
            
            with engine.begin() as _conn:
                _conn.execute(update_customerRegistration)
                        
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Successful SignUp Request",
                Details=f"{data.user_id.lower()} has succeded to add a SignUp Request.",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
        else:
            # Remove User from CustomerUserProfile
            delete_customerUserProfile = customerUserProfile.delete().where(
                                customerUserProfile.c.USER_ID == data.user_id.lower()
                            )
            
            with engine.begin() as _conn:
                _conn.execute(delete_customerUserProfile)
            
            # Update SignUp Request to DECLINED
            update_customerRegistration = customerRegistration.update().values(
                                STATUS="DECLINED"
                            ).where(
                                and_(
                                    customerRegistration.c.BRANCH_ID == cbs_customer_full_info.customer.branch_code,
                                    customerRegistration.c.USER_ID == data.user_id.lower(),
                                    customerRegistration.c.CUSTOMER_ID == data.customer_id,
                                    customerRegistration.c.TAX_ID == data.tax_id,
                                    customerRegistration.c.PHONE_NUMBER == data.phone_number,
                                    customerRegistration.c.BIRTH_DATE == data.birth_date,
                                    customerRegistration.c.STATUS == "PENDING"
                                )
                            )
            
            with engine.begin() as _conn:
                _conn.execute(update_customerRegistration)
        
            AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
        return status
    
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="RegistrationRoutes/SignUp",
            CreatedBy=""
        ))
        AddActivityLog(SystemActivitySchema(
                Type="SELF-SIGNUP",
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
        
        return status
        
