from datetime import datetime
import traceback
from fastapi import APIRouter
from sqlalchemy import and_, func, or_
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from Models.shared import customerRegistration, customerUserProfile
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemLogErrorSchema, SystemActivitySchema, RegistrationViewModelSchema, CustomerOtpSchema, CustomerUserProfileSchema
from Services.CaptchaService import DisableCaptchaToken, VerifyCaptchaToken
from Services.GenericCRUDServices import GenericInserter
from Services.LogServices import AddLogOrError
from Services.ActivityServices import AddActivityLog
from Cache.AppSettingsCache import Get
from Services.CommonServices import ConvertToBool, GetSha1Hash, GetEncryptedText, GetTableSl, SendCredentials, GetErrorMessage
from Services.CBSServices import GetCustomerFullInformation
from Services.OTPServices import GenerateCode, Authentication

RegistrationRoutes = APIRouter(prefix="/Registration")

@RegistrationRoutes.get("/IsUserIDAvailable")
async def IsUserIDAvailable(user_id: str) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        
        result = await db_session.execute(
            customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == user_id.lower())
        )
        if result is not None:
            user_profile = result.fetchone()
        
        status.Status = "OK"
        status.Message = None
        status.Result = not bool(user_profile)
        
        return status
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        return status
    finally:
        if db_session:
            await db_session.close()

@RegistrationRoutes.post("/SignUp")
async def SignUp(data:RegistrationViewModelSchema) -> StatusResult:
    status = StatusResult[object]()
    db_session = None
    try:
        isHuman = await VerifyCaptchaToken(data.captcha_token)
        if not isHuman:
            raise ValueError("CAPTCHA verification failed.")
        
        db_session = AsyncSessionLocalClickNet()
        # UserID Setting
        if not await ConvertToBool(Get("AUTO_SET_USER_ID_AT_SIGNUP")):
            if not data.user_id:
                raise ValueError("User ID is required.")
        else:
            user_id_type = Get("AUTO_SET_USER_ID_TYPE_AT_SIGNUP").upper()
            
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
        result = await db_session.execute(
            customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == data.user_id.lower())
        )
        if result is not None:
            existing_user = result.fetchone()
        
        if existing_user:
            raise ValueError("System does not allow same userid for multiple user.")
        
        # Get CBS Data By CustomerID
        cbs_customer_full_info = await GetCustomerFullInformation(data.customer_id)
        
        if not cbs_customer_full_info:
            raise ValueError("Invalid Customer ID.")
        
        # Checking Customer
        result = await db_session.execute(
            customerUserProfile.select().where(customerUserProfile.c.CUSTOMER_ID == data.customer_id)
        )
        if result is not None:
            existing_user = result.fetchone()
        if existing_user:
            raise ValueError("System does not allow multiple user for Individual type customer.")
        
        if await ConvertToBool(Get("RESTRICT_SAME_MOBILE_NO_AT_SIGNUP")):
            result = await db_session.execute(
                customerUserProfile.select().where(customerUserProfile.c.MOBILE_NUMBER_HASH == GetSha1Hash(data.phone_number))
            )
            if result is not None:
                existing_users_same_mobile = result.fetchone()
            if existing_users_same_mobile:
                raise ValueError("System does not allow same mobile number for multiple user.")
        
        # Check Data with CBS
        # Customer ID Checking
        if data.customer_id != cbs_customer_full_info.customer.customer_id:
            raise ValueError("Invalid Customer ID.")
            
        
        # Birth Date Checking
        if not data.birth_date or data.birth_date.strftime("%d/%m/%Y") == "01/01/0001":
            raise ValueError("Date of Birth is required.")
        
        if cbs_customer_full_info.customer.birth_date:
            if data.birth_date.strftime("%d-%b-%Y") != cbs_customer_full_info.customer.birth_date.strftime("%d-%b-%Y"):
                raise ValueError("Invalid Date of Birth.")
        else:
            raise ValueError("No Date of Birth found in CBS. Please contact with your branch for further details")
        
        # TaxID Checking
        if not data.tax_id:
            raise ValueError("Verification ID is required.")
        
        if cbs_customer_full_info.customer.tax_id:                
            if data.tax_id != cbs_customer_full_info.customer.tax_id:
                raise ValueError("Invalid Verification ID for " + cbs_customer_full_info.customer.tax_id_type+".")
        else:
            raise ValueError("No verification ID information found in CBS. Please contact with your branch for further details")
        
        # Email Checking
        if cbs_customer_full_info.emails:
            validEmail = False
            for item in cbs_customer_full_info.emails:
                if data.email and data.email.strip():
                    if data.email == item.address:
                        validEmail = True
                        break
            
            if data.email and data.email.strip() and not validEmail:
                raise ValueError("Invalid Email.")
                
        
        # Mobile No Checking
        if not data.phone_number:
            raise ValueError("Mobile Number is required.")
        
        if cbs_customer_full_info.phones:
            validPhone = False
            for item in cbs_customer_full_info.phones:
                if data.phone_number == item.number:
                    validPhone = True
                    break
            
            if not validPhone:
                raise ValueError("Invalid Mobile Number.")
        else:
            raise ValueError("Update Mobile Number in CBS First.")
        
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
        result = await db_session.execute(
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
        )
        
        previousSignUpRequests = result.fetchall()
        if previousSignUpRequests:
            raise ValueError("The provided credentials are already in use. Please contact with the administrator.")
        
        # Save SignUp Request
        await db_session.execute(customerRegistration.insert().values(
                ID= await GetTableSl("customerRegistration"),
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
        )
        await db_session.commit()
        
        # Include User in CustomerUserProfile
        plain_password = await GenerateCode()
        new_user_profile = CustomerUserProfileSchema(
            user_id=data.user_id.lower(),
            user_nm=cbs_customer_full_info.customer.name.upper(),
            user_descrip="Self Sign In",
            password_string=await GetSha1Hash(plain_password),
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
            email_address=await GetEncryptedText(data.email),
            email_address_hash=await GetSha1Hash(data.email),
            mobile_number=await GetEncryptedText(data.phone_number),
            mobile_number_hash=await GetSha1Hash(data.phone_number),
            authentication_type=Get("DEFAULT_AUTHENTICATION_TYPE"),
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
        
        await GenericInserter[CustomerUserProfileSchema].insert_record(
            table=customerUserProfile,
            schema_model=CustomerUserProfileSchema,
            data=new_user_profile,
            returning_fields=[],
            async_session=db_session
        )

        status = await SendCredentials(new_user_profile, "SIGNUP", plain_password)
        
        if status.Status == "OK":
            # Update SignUp Request to PROCESSED
            await db_session.execute(customerRegistration.update().values(
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
            )
            await db_session.commit()
                        
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.SIGNUP,
                Title="Successful SignUp Request",
                Details=f"{data.user_id.lower()} has succeded to add a SignUp Request.",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
            
        else:
            # Remove User from CustomerUserProfile
            await db_session.execute(customerUserProfile.delete().where(
                    customerUserProfile.c.USER_ID == data.user_id.lower()
                )
            )
            await db_session.commit()
            
            # Update SignUp Request to DECLINED
            await db_session.execute(customerRegistration.update().values(
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
            )
            await db_session.commit()
        
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.SIGNUP,
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
    
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="RegistrationRoutes/SignUp",
            CreatedBy=""
        ))
        await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.SIGNUP,
                Title="Failed to add a SignUp Request",
                Details=f"{data.user_id.lower()} has failed to add a SignUp Request. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=data.user_id.lower()
            ))
    
    finally:
        if db_session:
            await db_session.close()
        
    await DisableCaptchaToken(data.captcha_token)
    return status
