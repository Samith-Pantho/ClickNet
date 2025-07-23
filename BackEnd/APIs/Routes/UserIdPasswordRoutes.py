from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from Config.dbConnection import engine 
from Models.shared import customerPasswordHist, customerUserProfile
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema,ChangePasswordViewModelSchema, ForgetPasswordViewModelSchema, CustomerPasswordHistSchema, ForgetUserIdViewModelSchema, CustomerOtpSchema, CustomerUserProfileSchema
from Services.ActivityServices import AddActivityLog
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.AppSettingsServices import FetchAppSettingsByKey
from Services.CommonServices import GetSha1Hash, GetDecryptedText, ConvertToBool, GetCurrentActiveSession, GetErrorMessage, SendCredentials, SendEmail, SendSMS
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.OTPServices import Authentication, GenerateCode
from Services.CBSServices import GetCustomerFullInformation

restricted = FetchAppSettingsByKey("RESTRICT_SPECIAL_CHARACTERS_FOR_PASSWORD")
PassLengthMax  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MAX_PASSWORD_LENGTH"))
PassLengthMin  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_PASSWORD_LENGTH"))
ForgetPasswordFailedAttemptsLimit  = int(FetchAppSettingsByKey("FORGET_PASSWORD_FAILED_ATTEMPTS_LIMIT"))
ForgetUserIdFailedAttemptsLimit  = int(FetchAppSettingsByKey("FORGET_USERID_FAILED_ATTEMPTS_LIMIT"))
NonAlphaNumCharMin  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_NON_ALPHA_NUMERIC_CHAR_COUNT"))
SamePassReuseMax  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MAX_SAME_PASSWORD_REUSE_COUNT"))
SamePassRepeatAllowAfter  = int(FetchAppSettingsByKey("PASSWORD_POLICY_SAME_PASSWORD_REPEAT_ALLOWED_AFTER_DAYS"))
PassIsAlphanumeric  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_ALPHA_NUMERIC_CHAR_COUNT"))
PassSuccSameCharAllow = int(FetchAppSettingsByKey("PASSWORD_POLICY_SUCCESSIVE_SAME_CHAR_ALLOEWD_COUNT"))
CapitalCharMin  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_CAPITAL_CHAR_COUNT"))
SmallCharMin  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_SMALL_CHAR_COUNT"))
NumberMin  = int(FetchAppSettingsByKey("PASSWORD_POLICY_MIN_NUMBER_COUNT"))
DobVerificationMendatoryAtForgetPassword= FetchAppSettingsByKey("DOB_VERIFICATION_MENDATORY_AT_FORGET_PASSWORD")
MobileVerificationMendatoryAtForgetPassword= FetchAppSettingsByKey("MOBILE_MENDATORY_AT_FORGET_PASSWORD")
TaxidVerificationMendatoryAtForgetPassword= FetchAppSettingsByKey("TAXID_MENDATORY_AT_FORGET_PASSWORD")
DobVerificationMendatoryAtForgetUserId= FetchAppSettingsByKey("DOB_VERIFICATION_MENDATORY_AT_FORGET_USERID")
MobileVerificationMendatoryAtForgetUserId= FetchAppSettingsByKey("MOBILE_MENDATORY_AT_FORGET_USERID")
TaxidVerificationMendatoryAtForgetUserId= FetchAppSettingsByKey("TAXID_MENDATORY_AT_FORGET_USERID")
AutoGeneretedPasswordAtForgetPassword = FetchAppSettingsByKey("AUTO_GENARATED_PASSWORD")
AutoUserActivationAtForgetPassword = FetchAppSettingsByKey("AUTO_USER_ACTIVATION_AFTER_FORGET_PASSWORD")

UserIdPasswordRoutes = APIRouter(prefix="/UserIdPassword")

customerUserProfileUpdater = GenericUpdater[CustomerUserProfileSchema, type(customerUserProfile)]()

def _CheckSpecialCharacter(new_password: str):
    if restricted:
        restricted_list = restricted.split("-----")
        for char in restricted_list:
            if char and char in new_password:
                return f"Choose other special character instead of {char}\n"
    return ""

def _CheckSuccessivecharacters(password: str) -> bool:
    count = 1
    last_char = ''
    for c in password:
        if c == last_char:
            count += 1
            if count > PassSuccSameCharAllow:
                return True
        else:
            count = 1
            last_char = c
    return False

def _CheckPasswordPolicy(plain_password:str, user_id:str) -> StatusResult:
    status = StatusResult[object]()
    msg = ""
    # Password length
    if not (PassLengthMin <= len(plain_password) <= PassLengthMax):
        msg += f"Password must be between {PassLengthMin} and {PassLengthMax} characters.\n"

    # Numeric
    if sum(c.isdigit() for c in plain_password) < NumberMin:
        msg += f"Password must contain at least {NumberMin} numeric character(s).\n"

    # Uppercase
    if sum(c.isupper() for c in plain_password) < CapitalCharMin:
        msg += f"Password must contain at least {CapitalCharMin} uppercase character(s).\n"

    # Lowercase
    if sum(c.islower() for c in plain_password) < SmallCharMin:
        msg += f"Password must contain at least {SmallCharMin} lowercase character(s).\n"

    # Alphanumeric characters
    if sum(1 for c in plain_password if c.isalnum()) < PassIsAlphanumeric:
        msg += f"Password must contain at least {PassIsAlphanumeric} alphanumeric character(s).\n"

    # Special characters
    if sum(1 for c in plain_password if not c.isalnum()) < NonAlphaNumCharMin:
        msg += f"Password must contain at least {NonAlphaNumCharMin} special character(s).\n"

    # Reuse check
    reused_count = 0
    with engine.connect() as _conn:
        result = _conn.execute(customerPasswordHist.select().where(func.lower(customerPasswordHist.c.USER_ID) == user_id.lower()))
    
    password_history = [CustomerPasswordHistSchema(**dict(row._mapping)) for row in result.fetchall()]
    
    for old in password_history:
        if old.passward_string == GetSha1Hash(plain_password):
            reused_count += 1
            if old.create_dt:
                reused_allowed_dt = old.create_dt + timedelta(days=SamePassRepeatAllowAfter)
                if reused_allowed_dt > datetime.now():
                    msg += f"This password was used recently and cannot be reused until {reused_allowed_dt.strftime('%d-%b-%Y')}.\n"

    if reused_count > SamePassReuseMax:
        msg += f"This password has been used {reused_count} times. Reuse limit is {SamePassReuseMax}.\n"

    # Check for too many successive same characters
    if _CheckSuccessivecharacters(plain_password):
        msg += f"Password must not contain more than {PassSuccSameCharAllow} successive repeating characters.\n"

    # Custom special character rule (optional)
    special_msg = _CheckSpecialCharacter(plain_password)
    if special_msg != "":
        msg += special_msg

    if msg != "":
        status.Status = "FAILED"
        status.Message = msg
        status.Result = None
    else:
        status.Status = "OK"
        status.Message = None
        status.Result = None
    
    return status

@UserIdPasswordRoutes.post("/ChangePassword")
def ChangePassword(data: ChangePasswordViewModelSchema, currentCustuserprofile=Depends(ValidateJWTToken)):
    status = StatusResult[object]()
    status.Message = "Failed to change password"
    try:
        session = GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Trying to change password",
            Details=f"{data.UserID.lower()} is trying to change password",
            IpAddress=session.ip_address,
            UserType="USER",
            User_Id=session.create_by
        ))

        if currentCustuserprofile.user_id.lower() != data.UserID.lower():
            raise ValueError("Wrong User ID")

        if data.NewPassword != data.ConfirmNewPassword:
            raise ValueError("Confirm password mismatched")

        if data.OldPassword == data.NewPassword:
            raise ValueError("Old password and new password cannot be same")

        if currentCustuserprofile.password_string == GetSha1Hash(data.OldPassword):
            status = _CheckPasswordPolicy(data.NewPassword, currentCustuserprofile.user_id.lower())
            if status.Status != "OK":
                return status

            old_pass_hist = CustomerPasswordHistSchema(
                user_id=currentCustuserprofile.user_id.lower(),
                passward_string=currentCustuserprofile.password_string,
                create_by=currentCustuserprofile.user_id.lower(),
                create_dt=datetime.now(),
                status=1
            )
            GenericInserter[CustomerPasswordHistSchema].insert_record(
                table=customerPasswordHist,
                schema_model=CustomerPasswordHistSchema,
                data=old_pass_hist,
                returning_fields=[]
            )

            currentCustuserprofile.password_string = GetSha1Hash(data.NewPassword)
            currentCustuserprofile.last_password_changed_on = datetime.now()
            currentCustuserprofile.force_password_changed_flag = 0
            currentCustuserprofile.failed_login_attempts_nos = 0
            currentCustuserprofile.failed_pasword_recovery_attempts_nos = 0
            currentCustuserprofile.failed_userid_recovery_attempts_nos = 0
            currentCustuserprofile.last_action = "EDT"
            currentCustuserprofile.recent_alert_msg = ""
            
            customerUserProfileUpdater.update_record(
                table=customerUserProfile,
                schema_model=CustomerUserProfileSchema,
                record_id=currentCustuserprofile.user_id,
                update_data=currentCustuserprofile,
                id_column="USER_ID",
                exclude_fields={} 
            )
            
            AddActivityLog(SystemActivitySchema(
                Type="SECURITYUPDATE",
                Title="Changed password successfully",
                Details=f"{data.UserID.lower()} has changed password successfully",
                IpAddress=session.ip_address,
                UserType="USER",
                User_Id=session.create_by
            ))
            
            
            status.Status = "OK"
            status.Message = "Successfully changed password"
            status.Result = None
        
            return status
        else:
            raise ValueError("Current password is incorrect")
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="PasswordRoutes/ChangePassword",
            CreatedBy=""
        ))
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Failed to change password",
            Details=f"{data.UserID.lower()} has failed to change password. Reason: {status.Message}",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        
        return status

async def _ResetPassword(data: ForgetPasswordViewModelSchema, user_profile: CustomerUserProfileSchema) -> StatusResult:
    status = StatusResult()
    new_password = ""
    try:
        if not ConvertToBool(AutoGeneretedPasswordAtForgetPassword):
            new_password = data.Newpassword
        else:
            new_password = GenerateCode()

        # Save Password History
        old_pass_hist = CustomerPasswordHistSchema(
            user_id=user_profile.user_id.lower(),
            passward_string=user_profile.password_string,
            create_by=user_profile.user_id.lower(),
            create_dt=datetime.now(),
            status=1
        )
        GenericInserter[CustomerPasswordHistSchema].insert_record(
            table=customerPasswordHist,
            schema_model=CustomerPasswordHistSchema,
            data=old_pass_hist,
            returning_fields=[]
        )

        # Update User Password Info
        encrypted_pw = GetSha1Hash(new_password)
        user_profile.password_string = encrypted_pw
        user_profile.last_password_changed_on = datetime.now()
        user_profile.last_action = "EDT"
        user_profile.recent_alert_msg = ""
        user_profile.failed_login_attempts_nos = 0
        user_profile.failed_pasword_recovery_attempts_nos = 0
        user_profile.failed_userid_recovery_attempts_nos = 0

        if ConvertToBool(AutoGeneretedPasswordAtForgetPassword):
            user_profile.force_password_changed_flag = 1
        else:
            user_profile.force_password_changed_flag = 0
                
        if ConvertToBool(AutoUserActivationAtForgetPassword):
            user_profile.user_status_active_flag = 1
            user_profile.last_activation_by = user_profile.user_id.lower()
            user_profile.last_activation_dt = datetime.now()

        customerUserProfileUpdater.update_record(
                table=customerUserProfile,
                schema_model=CustomerUserProfileSchema,
                record_id=user_profile.user_id,
                update_data=user_profile,
                id_column="USER_ID",
                exclude_fields={} 
            )

        status = await SendCredentials(user_profile, "FORGET_PASSWORD", new_password)
        
        return status
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="PasswordRoutes/_ResetPassword",
            CreatedBy=""
        ))
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Failed to reset password",
            Details=f"{data.UserID.lower()} is failed to reset password.",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        return status

@UserIdPasswordRoutes.post("/ForgetPassword")
async def ForgetPassword(data: ForgetPasswordViewModelSchema):
    status = StatusResult()
    user_profile = CustomerUserProfileSchema()
    try:
        with engine.connect() as _conn:
            result = _conn.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == data.UserID.lower())).first()
        
            if result:
                user_profile = CustomerUserProfileSchema(**dict(result._mapping))
            else:
                user_profile = None
                
        if not user_profile:
            raise ValueError("Wrong User ID.")
        
        if user_profile.locked_flag == 1:
            raise ValueError(user_profile.locked_reason or "Account is Locked.")

        if user_profile.customer_id != data.CustomerID:
            raise ValueError("Invalid User.")
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Trying to reset password",
            Details=f"{data.UserID.lower()} is trying to reset password.",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        
        try:
            customer_info = GetCustomerFullInformation(user_profile.customer_id)

            if ConvertToBool(DobVerificationMendatoryAtForgetPassword):
                if data.BirthDate.strftime("%d-%b-%Y") != customer_info.customer.birth_date.strftime("%d-%b-%Y"):
                    raise ValueError("Wrong Date of Birth.")

            registered_email = GetDecryptedText(user_profile.email_address).strip().lower()
            registered_mobile = GetDecryptedText(user_profile.mobile_number).strip()

            if ConvertToBool(MobileVerificationMendatoryAtForgetPassword):
                if data.Phone.strip() != registered_mobile:
                    raise ValueError("Wrong Mobile Number.")
                
            if ConvertToBool(TaxidVerificationMendatoryAtForgetPassword):
                if data.TaxID.strip() != customer_info.customer.tax_id:
                    raise ValueError("Wrong Tax ID.")
                
            if data.Email:
                if data.Email.strip().lower() != registered_email:
                    raise ValueError("Wrong Email Address.")

            if not ConvertToBool(AutoGeneretedPasswordAtForgetPassword):
                if not data.Newpassword and not data.ConfirmNewPassword:
                    raise ValueError("New Password is Needed.")
                
                if data.NewPassword != data.ConfirmNewPassword:
                    raise ValueError("Confirm password mismatched.")
                
                status = _CheckPasswordPolicy(data.Newpassword, user_profile.user_id.lower())
                if status.Status != "OK":
                    return status

            # OTP/TPIN verification
            status = await Authentication(CustomerOtpSchema(
                user_id=user_profile.user_id.lower(),
                cust_id=user_profile.customer_id,
                phone_number=registered_mobile,
                email_address=registered_email,
                verification_channel=data.OTP_verify_channel,
                otp=data.OTP
            ))
            
            if  status.Status.upper() != "OK":
                return status

            # Reset Password
            status = await _ResetPassword(data, user_profile)
            if status.Status == "OK":
                AddActivityLog(SystemActivitySchema(
                    Type="SECURITYUPDATE",
                    Title="Reset password successfully",
                    Details=f"{data.UserID.lower()} is successful to reset password.",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.UserID.lower()
                ))
                return status
            else:
                raise ValueError (status.Message)

        except Exception as ex:
            if user_profile:
                if user_profile.failed_pasword_recovery_attempts_nos < ForgetPasswordFailedAttemptsLimit:
                    user_profile.failed_pasword_recovery_attempts_nos += 1
                else:
                    user_profile.failed_pasword_recovery_attempts_nos = ForgetPasswordFailedAttemptsLimit
                    user_profile.locked_flag = 1
                    user_profile.locked_by=user_profile.user_id.lower()
                    user_profile.locked_dt=datetime.now()
                    user_profile.locked_reason=f"Account has been locked due to {ForgetPasswordFailedAttemptsLimit} times wrong attempts."
            
            if user_profile.locked_reason:
                raise ValueError(f"{ex}\n{user_profile.locked_reason}")
            else:
                raise ValueError(ex)
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="PasswordRoutes/ForgetPassword",
            CreatedBy=""
        ))
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Failed to reset password",
            Details=f"{data.UserID.lower()} is failed to reset password. Reason : " + GetErrorMessage(ex),
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        return status
    
@UserIdPasswordRoutes.post("/ForgetUserId")
async def ForgetUserId(data: ForgetUserIdViewModelSchema):
    status = StatusResult()
    user_profile = CustomerUserProfileSchema()
    try:
        with engine.connect() as _conn:
            result = _conn.execute(customerUserProfile.select().where(customerUserProfile.c.CUSTOMER_ID == data.CustomerID)).first()
        
            if result:
                user_profile = CustomerUserProfileSchema(**dict(result._mapping))
            else:
                user_profile = None
                
        if not user_profile:
            raise ValueError("Wrong Customer ID.")
        
        if user_profile.locked_flag == 1:
            raise ValueError(user_profile.locked_reason or "Account is Locked.")

        if user_profile.customer_id != data.CustomerID:
            raise ValueError("Invalid User.")
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Trying to fetch userid",
            Details=f"{user_profile.user_id.lower()} is trying to fetch userid.",
            IpAddress="",
            UserType="USER",
            User_Id=user_profile.user_id.lower()
        ))
        
        try:
            customer_info = GetCustomerFullInformation(user_profile.customer_id)

            if ConvertToBool(DobVerificationMendatoryAtForgetUserId):
                if data.BirthDate.strftime("%d-%b-%Y") != customer_info.customer.birth_date.strftime("%d-%b-%Y"):
                    raise ValueError("Wrong Date of Birth.")

            registered_email = GetDecryptedText(user_profile.email_address).strip().lower()
            registered_mobile = GetDecryptedText(user_profile.mobile_number).strip()

            if ConvertToBool(MobileVerificationMendatoryAtForgetUserId):
                if data.Phone.strip() != registered_mobile:
                    raise ValueError("Wrong Mobile Number.")
                
            if ConvertToBool(TaxidVerificationMendatoryAtForgetUserId):
                if data.TaxID.strip() != customer_info.customer.tax_id:
                    raise ValueError("Wrong Tax ID.")
                
            if data.Email:
                if data.Email.strip().lower() != registered_email:
                    raise ValueError("Wrong Email Address.")

            # OTP/TPIN verification
            status = await Authentication(CustomerOtpSchema(
                user_id=user_profile.user_id.lower(),
                cust_id=user_profile.customer_id,
                phone_number=registered_mobile,
                email_address=registered_email,
                verification_channel=data.OTP_verify_channel,
                otp=data.OTP
            ))
            
            if  status.Status.upper() != "OK":
                return status

            # Reset Failed attempts
            status = await SendCredentials(user_profile, "FORGET_USERID", None)
            
            if status.Status == "OK":
                user_profile.failed_userid_recovery_attempts_nos = 0

                customerUserProfileUpdater.update_record(
                        table=customerUserProfile,
                        schema_model=CustomerUserProfileSchema,
                        record_id=user_profile.user_id,
                        update_data=user_profile,
                        id_column="USER_ID",
                        exclude_fields={} 
                    )
            
                AddActivityLog(SystemActivitySchema(
                    Type="SECURITYUPDATE",
                    Title="Fetched userid successfully",
                    Details=f"{user_profile.user_id.lower()} is successful to fetch userid.",
                    IpAddress="",
                    UserType="USER",
                    User_Id=user_profile.user_id.lower()
                ))
                return status
            else:
                raise ValueError (status.Message)

        except Exception as ex:
            if user_profile:
                if user_profile.failed_userid_recovery_attempts_nos < ForgetUserIdFailedAttemptsLimit:
                    user_profile.failed_userid_recovery_attempts_nos += 1
                else:
                    user_profile.failed_userid_recovery_attempts_nos = ForgetUserIdFailedAttemptsLimit
                    user_profile.locked_flag = 1
                    user_profile.locked_by=user_profile.user_id.lower()
                    user_profile.locked_dt=datetime.now()
                    user_profile.locked_reason=f"Account has been locked due to {ForgetUserIdFailedAttemptsLimit} times wrong attempts."
                
                customerUserProfileUpdater.update_record(
                    table=customerUserProfile,
                    schema_model=CustomerUserProfileSchema,
                    record_id=user_profile.user_id,
                    update_data=user_profile,
                    id_column="USER_ID",
                    exclude_fields={} 
                )
            
            if user_profile.locked_reason:
                raise ValueError(f"{ex}\n{user_profile.locked_reason}")
            else:
                raise ValueError(ex)
    except Exception as ex:
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="PasswordRoutes/ForgetUserId",
            CreatedBy=""
        ))
        
        AddActivityLog(SystemActivitySchema(
            Type="SECURITYUPDATE",
            Title="Failed to reset password",
            Details=f"{data.CustomerID} is failed to reset password. Reason : " + GetErrorMessage(ex),
            IpAddress="",
            UserType="USER",
            User_Id="Anonymous"
        ))
        return status