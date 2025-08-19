from datetime import datetime, timedelta
import traceback
from fastapi import APIRouter, Depends
from sqlalchemy import func
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from Models.shared import customerPasswordHist, customerUserProfile
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema,ChangePasswordViewModelSchema, ForgetPasswordViewModelSchema, CustomerPasswordHistSchema, ForgetUserIdViewModelSchema, CustomerOtpSchema, CustomerUserProfileSchema
from Services.ActivityServices import AddActivityLog
from Services.CaptchaService import DisableCaptchaToken, VerifyCaptchaToken
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from Services.CommonServices import GetSha1Hash, GetDecryptedText, ConvertToBool, GetCurrentActiveSession, GetErrorMessage, SendCredentials
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.OTPServices import Authentication, GenerateCode
from Services.CBSServices import GetCustomerFullInformation

UserIdPasswordRoutes = APIRouter(prefix="/UserIdPassword")

customerUserProfileUpdater = GenericUpdater[CustomerUserProfileSchema, type(customerUserProfile)]()

def _CheckSpecialCharacter(new_password: str):
    restricted = Get("RESTRICT_SPECIAL_CHARACTERS_FOR_PASSWORD") 
    if restricted:
        restricted_list = restricted.split("-----")
        for char in restricted_list:
            if char and char in new_password:
                return f"Choose other special character instead of {char}\n"
    return ""

def _CheckSuccessivecharacters(password: str, PassSuccSameCharAllow:str) -> bool:
    count = 1
    last_char = ''
    for c in password:
        if c == last_char:
            count += 1
            if count > int(PassSuccSameCharAllow):
                return True
        else:
            count = 1
            last_char = c
    return False

async def _CheckPasswordPolicy(plain_password:str, user_id:str, db_session) -> StatusResult:
    status = StatusResult[object]()
    msg = ""
    PassLengthMax  = Get("PASSWORD_POLICY_MAX_PASSWORD_LENGTH")
    PassLengthMin  = Get("PASSWORD_POLICY_MIN_PASSWORD_LENGTH")
    NonAlphaNumCharMin  = Get("PASSWORD_POLICY_MIN_NON_ALPHA_NUMERIC_CHAR_COUNT")
    SamePassReuseMax  = Get("PASSWORD_POLICY_MAX_SAME_PASSWORD_REUSE_COUNT")
    SamePassRepeatAllowAfter  = Get("PASSWORD_POLICY_SAME_PASSWORD_REPEAT_ALLOWED_AFTER_DAYS")
    PassIsAlphanumeric  = Get("PASSWORD_POLICY_MIN_ALPHA_NUMERIC_CHAR_COUNT")
    PassSuccSameCharAllow = Get("PASSWORD_POLICY_SUCCESSIVE_SAME_CHAR_ALLOEWD_COUNT")
    CapitalCharMin  = Get("PASSWORD_POLICY_MIN_CAPITAL_CHAR_COUNT")
    SmallCharMin  = Get("PASSWORD_POLICY_MIN_SMALL_CHAR_COUNT")
    NumberMin  = Get("PASSWORD_POLICY_MIN_NUMBER_COUNT")

    # Password length
    if not (int(PassLengthMin) <= len(plain_password) <= int(PassLengthMax)):
        msg += f"Password must be between {int(PassLengthMin)} and {int(PassLengthMax)} characters.\n"

    # Numeric
    if sum(c.isdigit() for c in plain_password) < int(NumberMin):
        msg += f"Password must contain at least {int(NumberMin)} numeric character(s).\n"

    # Uppercase
    if sum(c.isupper() for c in plain_password) < int(CapitalCharMin):
        msg += f"Password must contain at least {int(CapitalCharMin)} uppercase character(s).\n"

    # Lowercase
    if sum(c.islower() for c in plain_password) < int(SmallCharMin):
        msg += f"Password must contain at least {int(SmallCharMin)} lowercase character(s).\n"

    # Alphanumeric characters
    if sum(1 for c in plain_password if c.isalnum()) < int(PassIsAlphanumeric):
        msg += f"Password must contain at least {int(PassIsAlphanumeric)} alphanumeric character(s).\n"

    # Special characters
    if sum(1 for c in plain_password if not c.isalnum()) < int(NonAlphaNumCharMin):
        msg += f"Password must contain at least {int(NonAlphaNumCharMin)} special character(s).\n"

    # Reuse check
    reused_count = 0
    result = await db_session.execute(customerPasswordHist.select().where(func.lower(customerPasswordHist.c.USER_ID) == user_id.lower()))
    rows = result.fetchall()
    password_history = [CustomerPasswordHistSchema(**dict(row._mapping)) for row in rows]
    
    for old in password_history:
        if old.passward_string == GetSha1Hash(plain_password):
            reused_count += 1
            if old.create_dt:
                reused_allowed_dt = old.create_dt + timedelta(days=int(SamePassRepeatAllowAfter))
                if reused_allowed_dt > datetime.now():
                    msg += f"This password was used recently and cannot be reused until {reused_allowed_dt.strftime('%d-%b-%Y')}.\n"

    if reused_count > int(SamePassReuseMax):
        msg += f"This password has been used {reused_count} times. Reuse limit is {int(SamePassReuseMax)}.\n"

    # Check for too many successive same characters
    if _CheckSuccessivecharacters(plain_password, PassSuccSameCharAllow):
        msg += f"Password must not contain more than {int(PassSuccSameCharAllow)} successive repeating characters.\n"

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
async def ChangePassword(data: ChangePasswordViewModelSchema, currentCustuserprofile=Depends(ValidateJWTToken)):
    status = StatusResult[object]()
    status.Message = "Failed to change password"
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
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

        if currentCustuserprofile.password_string == await GetSha1Hash(data.OldPassword):
            status = await _CheckPasswordPolicy(data.NewPassword, currentCustuserprofile.user_id.lower(), db_session)
            if status.Status != "OK":
                return status

            old_pass_hist = CustomerPasswordHistSchema(
                user_id=currentCustuserprofile.user_id.lower(),
                passward_string=currentCustuserprofile.password_string,
                create_by=currentCustuserprofile.user_id.lower(),
                create_dt=datetime.now(),
                status=1
            )
            await GenericInserter[CustomerPasswordHistSchema].insert_record(
                table=customerPasswordHist,
                schema_model=CustomerPasswordHistSchema,
                data=old_pass_hist,
                returning_fields=[]
            )

            currentCustuserprofile.password_string = await GetSha1Hash(data.NewPassword)
            currentCustuserprofile.last_password_changed_on = datetime.now()
            currentCustuserprofile.force_password_changed_flag = 0
            currentCustuserprofile.failed_login_attempts_nos = 0
            currentCustuserprofile.failed_pasword_recovery_attempts_nos = 0
            currentCustuserprofile.failed_userid_recovery_attempts_nos = 0
            currentCustuserprofile.last_action = "EDT"
            currentCustuserprofile.recent_alert_msg = ""
            
            await customerUserProfileUpdater.update_record(
                table=customerUserProfile,
                schema_model=CustomerUserProfileSchema,
                record_id=currentCustuserprofile.user_id,
                update_data=currentCustuserprofile,
                id_column="USER_ID",
                exclude_fields={}
            )
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.SECURITYUPDATE,
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
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="PasswordRoutes/ChangePassword",
            CreatedBy=""
        ))
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Failed to change password",
            Details=f"{data.UserID.lower()} has failed to change password. Reason: {status.Message}",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        
        return status
    finally:
        if db_session:
            await db_session.close()

async def _ResetPassword(data: ForgetPasswordViewModelSchema, user_profile: CustomerUserProfileSchema) -> StatusResult:
    status = StatusResult()
    new_password = ""
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        if not await ConvertToBool(Get("AUTO_GENARATED_PASSWORD")):
            new_password = data.Newpassword
        else:
            new_password = await GenerateCode()

        # Save Password History
        old_pass_hist = CustomerPasswordHistSchema(
            user_id=user_profile.user_id.lower(),
            passward_string=user_profile.password_string,
            create_by=user_profile.user_id.lower(),
            create_dt=datetime.now(),
            status=1
        )
        await GenericInserter[CustomerPasswordHistSchema].insert_record(
            table=customerPasswordHist,
            schema_model=CustomerPasswordHistSchema,
            data=old_pass_hist,
            returning_fields=[]
        )

        # Update User Password Info
        encrypted_pw = await GetSha1Hash(new_password)
        user_profile.password_string = encrypted_pw
        user_profile.last_password_changed_on = datetime.now()
        user_profile.last_action = "EDT"
        user_profile.recent_alert_msg = ""
        user_profile.failed_login_attempts_nos = 0
        user_profile.failed_pasword_recovery_attempts_nos = 0
        user_profile.failed_userid_recovery_attempts_nos = 0

        if await ConvertToBool(Get("AUTO_GENARATED_PASSWORD")):
            user_profile.force_password_changed_flag = 1
        else:
            user_profile.force_password_changed_flag = 0
                
        if await ConvertToBool(Get("AUTO_USER_ACTIVATION_AFTER_FORGET_PASSWORD")):
            user_profile.user_status_active_flag = 1
            user_profile.last_activation_by = user_profile.user_id.lower()
            user_profile.last_activation_dt = datetime.now()

        await customerUserProfileUpdater.update_record(
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
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="PasswordRoutes/_ResetPassword",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Failed to reset password",
            Details=f"{data.UserID.lower()} is failed to reset password.",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        return status
    finally:
        if db_session:
            await db_session.close()

@UserIdPasswordRoutes.post("/ForgetPassword")
async def ForgetPassword(data: ForgetPasswordViewModelSchema):
    status = StatusResult()
    user_profile = CustomerUserProfileSchema()
    db_session = None
    try:
        isHuman = await VerifyCaptchaToken(data.captcha_token)
        if not isHuman:
            raise ValueError("CAPTCHA verification failed.")
        
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == data.UserID.lower()))
        if result is not None:
            row = result.fetchone()
        if row:
            user_profile = CustomerUserProfileSchema(**dict(row._mapping))
        else:
            user_profile = None
                
        if not user_profile:
            raise ValueError("Wrong User ID.")
        
        if user_profile.locked_flag == 1:
            raise ValueError(user_profile.locked_reason or "Account is Locked.")

        if user_profile.customer_id != data.CustomerID:
            raise ValueError("Invalid User.")
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Trying to reset password",
            Details=f"{data.UserID.lower()} is trying to reset password.",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        
        try:
            DobVerificationMendatoryAtForgetPassword= Get("DOB_VERIFICATION_MENDATORY_AT_FORGET_PASSWORD")
            MobileVerificationMendatoryAtForgetPassword= Get("MOBILE_MENDATORY_AT_FORGET_PASSWORD")
            TaxidVerificationMendatoryAtForgetPassword= Get("TAXID_MENDATORY_AT_FORGET_PASSWORD")
            customer_info = await GetCustomerFullInformation(user_profile.customer_id)

            if await ConvertToBool(DobVerificationMendatoryAtForgetPassword):
                if data.BirthDate.strftime("%d-%b-%Y") != customer_info.customer.birth_date.strftime("%d-%b-%Y"):
                    raise ValueError("Wrong Date of Birth.")

            registered_email = (await GetDecryptedText(user_profile.email_address)).strip().lower()
            registered_mobile = (await GetDecryptedText(user_profile.mobile_number)).strip()

            if await ConvertToBool(MobileVerificationMendatoryAtForgetPassword):
                if data.Phone.strip() != registered_mobile:
                    raise ValueError("Wrong Mobile Number.")
                
            if await ConvertToBool(TaxidVerificationMendatoryAtForgetPassword):
                if data.TaxID.strip() != customer_info.customer.tax_id:
                    raise ValueError("Wrong Verification ID for " + customer_info.customer.tax_id_type +".")
                
            if data.Email:
                if data.Email.strip().lower() != registered_email:
                    raise ValueError("Wrong Email Address.")

            if not await ConvertToBool(Get("AUTO_GENARATED_PASSWORD")):
                if not data.Newpassword and not data.ConfirmNewPassword:
                    raise ValueError("New Password is Needed.")
                
                if data.NewPassword != data.ConfirmNewPassword:
                    raise ValueError("Confirm password mismatched.")
                
                status = await _CheckPasswordPolicy(data.Newpassword, user_profile.user_id.lower(), db_session)
                if status.Status != "OK":
                    raise ValueError(status.Message)

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
                await AddActivityLog(SystemActivitySchema(
                    Type=ActivityType.SECURITYUPDATE,
                    Title="Reset password successfully",
                    Details=f"{data.UserID.lower()} is successful to reset password.",
                    IpAddress="",
                    UserType="USER",
                    User_Id=data.UserID.lower()
                ))
            else:
                raise ValueError (status.Message)

        except Exception as ex:
            if user_profile:
                ForgetPasswordFailedAttemptsLimit  = Get("FORGET_PASSWORD_FAILED_ATTEMPTS_LIMIT")
                if user_profile.failed_pasword_recovery_attempts_nos < int(ForgetPasswordFailedAttemptsLimit):
                    user_profile.failed_pasword_recovery_attempts_nos += 1
                else:
                    user_profile.failed_pasword_recovery_attempts_nos = int(ForgetPasswordFailedAttemptsLimit)
                    user_profile.locked_flag = 1
                    user_profile.locked_by=user_profile.user_id.lower()
                    user_profile.locked_dt=datetime.now()
                    user_profile.locked_reason=f"Account has been locked due to {int(ForgetPasswordFailedAttemptsLimit)} times wrong attempts."
            
            await customerUserProfileUpdater.update_record(
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
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="PasswordRoutes/ForgetPassword",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Failed to reset password",
            Details=f"{data.UserID.lower()} is failed to reset password. Reason : " + await GetErrorMessage(ex),
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
    finally:
        if db_session:
            await db_session.close()
            
    await DisableCaptchaToken(data.captcha_token)
    return status
    
@UserIdPasswordRoutes.post("/ForgetUserId")
async def ForgetUserId(data: ForgetUserIdViewModelSchema):
    status = StatusResult()
    user_profile = CustomerUserProfileSchema()
    db_session = None
    try:
        isHuman = await VerifyCaptchaToken(data.captcha_token)
        if not isHuman:
            raise ValueError("CAPTCHA verification failed.")
        
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(customerUserProfile.select().where(customerUserProfile.c.CUSTOMER_ID == data.CustomerID))
        if result is not None:
            row = result.fetchone()
        if row:
            user_profile = CustomerUserProfileSchema(**dict(row._mapping))
        else:
            user_profile = None
                
        if not user_profile:
            raise ValueError("Wrong Customer ID.")
        
        if user_profile.locked_flag == 1:
            raise ValueError(user_profile.locked_reason or "Account is Locked.")

        if user_profile.customer_id != data.CustomerID:
            raise ValueError("Invalid User.")
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Trying to fetch userid",
            Details=f"{user_profile.user_id.lower()} is trying to fetch userid.",
            IpAddress="",
            UserType="USER",
            User_Id=user_profile.user_id.lower()
        ))
        
        try:
            DobVerificationMendatoryAtForgetUserId= Get("DOB_VERIFICATION_MENDATORY_AT_FORGET_USERID")
            MobileVerificationMendatoryAtForgetUserId= Get("MOBILE_MENDATORY_AT_FORGET_USERID")
            TaxidVerificationMendatoryAtForgetUserId= Get("TAXID_MENDATORY_AT_FORGET_USERID")
            customer_info = await GetCustomerFullInformation(user_profile.customer_id)

            if ConvertToBool(DobVerificationMendatoryAtForgetUserId):
                if data.BirthDate.strftime("%d-%b-%Y") != customer_info.customer.birth_date.strftime("%d-%b-%Y"):
                    raise ValueError("Wrong Date of Birth.")

            registered_email = (await GetDecryptedText(user_profile.email_address)).strip().lower()
            registered_mobile = (await GetDecryptedText(user_profile.mobile_number)).strip()

            if await ConvertToBool(MobileVerificationMendatoryAtForgetUserId):
                if data.Phone.strip() != registered_mobile:
                    raise ValueError("Wrong Mobile Number.")
                
            if await ConvertToBool(TaxidVerificationMendatoryAtForgetUserId):
                if data.TaxID.strip() != customer_info.customer.tax_id:
                    raise ValueError("Wrong Verification ID for " + customer_info.customer.tax_id_type+".")
                
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

            status = await SendCredentials(user_profile, "FORGET_USERID", None)
            
            if status.Status == "OK":
                user_profile.failed_userid_recovery_attempts_nos = 0

                await customerUserProfileUpdater.update_record(
                        table=customerUserProfile,
                        schema_model=CustomerUserProfileSchema,
                        record_id=user_profile.user_id,
                        update_data=user_profile,
                        id_column="USER_ID",
                        exclude_fields={}
                    )
            
                await AddActivityLog(SystemActivitySchema(
                    Type=ActivityType.SECURITYUPDATE,
                    Title="Fetched userid successfully",
                    Details=f"{user_profile.user_id.lower()} is successful to fetch userid.",
                    IpAddress="",
                    UserType="USER",
                    User_Id=user_profile.user_id.lower()
                ))
            else:
                raise ValueError(status.Message)

        except Exception as ex:
            if user_profile:
                ForgetUserIdFailedAttemptsLimit  = Get("FORGET_USERID_FAILED_ATTEMPTS_LIMIT")
                if user_profile.failed_userid_recovery_attempts_nos < int(ForgetUserIdFailedAttemptsLimit):
                    user_profile.failed_userid_recovery_attempts_nos += 1
                else:
                    user_profile.failed_userid_recovery_attempts_nos = int(ForgetUserIdFailedAttemptsLimit)
                    user_profile.locked_flag = 1
                    user_profile.locked_by=user_profile.user_id.lower()
                    user_profile.locked_dt=datetime.now()
                    user_profile.locked_reason=f"Account has been locked due to {int(ForgetUserIdFailedAttemptsLimit)} times wrong attempts."
                
                await customerUserProfileUpdater.update_record(
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
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="PasswordRoutes/ForgetUserId",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.SECURITYUPDATE,
            Title="Failed to reset password",
            Details=f"{data.CustomerID} is failed to reset password. Reason : " + await GetErrorMessage(ex),
            IpAddress="",
            UserType="USER",
            User_Id="Anonymous"
        ))
    finally:
        if db_session:
            await db_session.close()
    
    await DisableCaptchaToken(data.captcha_token)
    return status