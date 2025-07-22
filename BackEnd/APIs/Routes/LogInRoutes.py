import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, func
from Config.dbConnection import engine 
from Models.shared import customerUserProfile, customerSession, customerOTP
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema,LoginViewModelSchema, CustomerUserProfileSchema, CustomoerSessionSchema, NotificationViewModelSchema, CustomerOtpSchema
from Services.ActivityServices import AddActivityLog
from Services.JWTTokenServices import GenerateJWTToken
from Services.LogServices import AddLogOrError
from Services.AppSettingsServices import FetchAppSettingsByKey
from Services.CommonServices import GetSha1Hash, GetDecryptedText, ConvertToBool, SendNotification, GetErrorMessage
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.OTPServices import Authentication

system_down = FetchAppSettingsByKey("SYSTEM_DOWN")
system_down_msg = FetchAppSettingsByKey("SYSTEM_DOWN_MSG")
enable_licence_checking = FetchAppSettingsByKey("ENABLE_LICENCE_CHECKING")
notifications_sending_process = FetchAppSettingsByKey("NOTIFICATIONS_SENDING_PROCESS").upper()
login_after_otp_verification = FetchAppSettingsByKey("LOGIN_AFTER_OTP_VERIFICATION")
password_expiry_days = float(FetchAppSettingsByKey("PASSWORD_EXPIRY_DAYS"))
auto_user_activation_after_forget_password = FetchAppSettingsByKey("AUTO_USER_ACTIVATION_AFTER_FORGET_PASSWORD")
login_wrong_password_attempt_limit = int(FetchAppSettingsByKey("LOGIN_WRONG_PASSWORD_ATTEMPT_LIMIT"))

customerUserProfileUpdater = GenericUpdater[CustomerUserProfileSchema, type(customerUserProfile)]()
customerSessionUpdater = GenericUpdater[CustomoerSessionSchema, type(customerSession)]()

LogInRoutes = APIRouter(prefix="/Login")

def _CheckLoginCredentials(data: LoginViewModelSchema) -> CustomerUserProfileSchema:
    try:
        user_profile = CustomerUserProfileSchema()
        
        if data:
            with engine.connect() as _conn:
                result = _conn.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == data.UserID.lower())).first()
            
                if result:
                    user_profile = CustomerUserProfileSchema(**dict(result._mapping))
            
            if user_profile:
                if user_profile.password_string:
                    if GetSha1Hash(data.Password) == user_profile.password_string:
                        
                        if not user_profile.user_profile_closed_flag:
                            if not user_profile.locked_flag:
                                if user_profile.user_status_active_flag:
                                    user_profile.recent_alert_msg = ""
                                    user_profile.failed_login_attempts_nos = 0
                                    user_profile.failed_pasword_recovery_attempts_nos = 0
                                    user_profile.failed_userid_recovery_attempts_nos = 0
                                    
                                    if user_profile.last_password_changed_on:
                                        password_expiry_date = user_profile.last_password_changed_on + timedelta(days=password_expiry_days)
                                    
                                        if datetime.now() > password_expiry_date:
                                            user_profile.force_password_changed_flag = True
                                    else:
                                        user_profile.last_password_changed_on = user_profile.last_signed_on
                                    
                                    user_profile.last_signed_on = datetime.now()
                                    
                                    return customerUserProfileUpdater.update_record(
                                        table=customerUserProfile,
                                        schema_model=CustomerUserProfileSchema,
                                        record_id=user_profile.user_id,
                                        update_data=user_profile,
                                        id_column="USER_ID",
                                        exclude_fields={} 
                                    )
                                else:
                                    user_profile.recent_alert_msg = "Your account has been deactivated. Please Change Password for reactivation."
                            else:
                                user_profile.recent_alert_msg = "Your account has been Locked."
                        else:
                            if not user_profile.recent_alert_msg:
                                user_profile.recent_alert_msg = "Your account has been closed."
                    else:
                        if user_profile.failed_login_attempts_nos < login_wrong_password_attempt_limit:
                            user_profile.failed_login_attempts_nos += 1
                            user_profile.recent_alert_msg = f"Wrong Password attempt {user_profile.failed_login_attempts_nos} times."
                        
                        if user_profile.failed_login_attempts_nos == login_wrong_password_attempt_limit:
                            user_profile.recent_alert_msg = (
                                f"Your account has been deactivated due to {login_wrong_password_attempt_limit} times wrong attempts."
                            )
                            user_profile.user_status_active_flag = False
                            user_profile.force_password_changed_flag = True
            else:
                return None
        
        return customerUserProfileUpdater.update_record(
            table=customerUserProfile,
            schema_model=CustomerUserProfileSchema,
            record_id=user_profile.user_id,
            update_data=user_profile,
            id_column="USER_ID",
            exclude_fields={} 
        )
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "LogInRoutes/_CheckLoginCredentials",
            CreatedBy = ""
        ))
        return None

def _create_session(access_token: str) -> bool:
    try:
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        user_id = GetDecryptedText(decoded_token.get("UserId"))
        session_id = GetDecryptedText(decoded_token.get("SessionID"))
        ip_Address = decoded_token.get("IpAddress")
        
        # Clear Previous User Session
        with engine.connect() as _conn:
            result = _conn.execute(
                customerSession.select().where(
                    and_(
                        func.lower(customerSession.c.USER_ID) == func.lower(user_id),
                        customerSession.c.ACTIVE_FLAG == 1
                    )
                )
            ).fetchall()
        previous_user_list = [CustomoerSessionSchema(**dict(row._mapping)) for row in result]
        
        if previous_user_list:
            for user_session in previous_user_list:
                user_session.active_flag = 0
                user_session.status = 0
                user_session.remarks = f"Logged out from {user_session.ip_address} by Application. Reason: session expired."
                customerSessionUpdater.update_record(
                    table=customerSession,
                    schema_model=CustomoerSessionSchema,
                    record_id=user_session.session_id,
                    update_data=user_session,
                    id_column="SESSION_ID",
                    exclude_fields={} 
                )
        
        # Create New user Session
        new_session = CustomoerSessionSchema(
            user_id=user_id.lower(),
            session_id=session_id,
            start_time=datetime.now(),
            last_access_time=datetime.now(),
            ip_address=ip_Address,
            active_flag=1,
            remarks=f"Logged in from {ip_Address}",
            status=1,
            create_by=user_id.lower(),
            create_dt=datetime.now()
        )
        
        try:
            GenericInserter[CustomoerSessionSchema].insert_record(
                table=customerSession,
                schema_model=CustomoerSessionSchema,
                data=new_session,
                returning_fields=[]
            )
            return True
        except Exception as er:
           AddLogOrError(SystemLogErrorSchema(
                Msg = str(ex),
                Type = "ERROR",
                ModuleName = "LogInRoutes/_create_session",
                CreatedBy = ""
            ))
           
        return False
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "LogInRoutes/_create_session",
            CreatedBy = ""
        ))
        return False

def _IsLoginSuccess(data: LoginViewModelSchema, cust_user_profile: CustomerUserProfileSchema) -> StatusResult:
    status = StatusResult()
    # Generate Token, Create Session for SuccessFull login
    access_token = GenerateJWTToken(cust_user_profile.user_id, data.IPAddress)
    
    if access_token and _create_session(access_token):
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        start_date = decoded_token.get("StartDate")
        expiry_date = decoded_token.get("ExpiryDate")
        
        login_response_model = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int((datetime.fromisoformat(expiry_date) - datetime.fromisoformat(start_date)).total_seconds() * 1000),
            "userName": cust_user_profile.user_id,
            "fullName": cust_user_profile.user_nm,
            "issued": start_date,
            "expires": expiry_date,
            "customerId": cust_user_profile.customer_id,
            "ForcePasswordChangedFlag":cust_user_profile.force_password_changed_flag
        }
        
        status.Status = "OK"
        status.Message = "Successfully logged in"
        status.Result = login_response_model
        
        AddActivityLog(SystemActivitySchema(
            Type="LOGIN",
            Title="Successfully logged in",
            Details=f"{cust_user_profile.user_id.lower()} is successfully logged in.",
            IpAddress="",
            UserType="USER",
            User_Id=cust_user_profile.user_id.lower()
        ))
    else:
        status.Status = "FAILED"
        status.Message = "Failed to create access token"
        status.Result = None
        
        AddActivityLog(SystemActivitySchema(
            Type="LOGIN",
            Title="Failed to Login",
            Details=f"{cust_user_profile.user_id.lower()} has failed to Login. Reason: {status.Message}",
            IpAddress="",
            UserType="USER",
            User_Id=cust_user_profile.user_id.lower()
        ))
    
    return status

@LogInRoutes.post("/Login")
async def Login(data: LoginViewModelSchema) -> StatusResult:
    status = StatusResult()
    cust_user_profile = CustomerUserProfileSchema()
    
    try:
        if ConvertToBool(system_down):
            status.Status = "FAILED"
            status.Message = system_down_msg
            status.Result = None
            return status
        
        
        # Licence Checking
        if ConvertToBool(enable_licence_checking):
            license_checking_msg = "" 
            if license_checking_msg:
                status.Status = "FAILED"
                status.Message = f"Licence Error: {license_checking_msg}"
                status.Result = None
                return status
        
        # Check user in DB
        cust_user_profile = _CheckLoginCredentials(data)
        
        if cust_user_profile:
            if cust_user_profile.recent_alert_msg:
                status.Status = "FAILED"
                status.Message = cust_user_profile.recent_alert_msg
                status.Result = None
                
                AddActivityLog(SystemActivitySchema(
                    Type="LOGIN",
                    Title="Failed to Login",
                    Details=f"{cust_user_profile.user_id.lower()} has failed to Login. Reason: {status.Message}",
                    IpAddress="",
                    UserType="USER",
                    User_Id=cust_user_profile.user_id.lower()
                ))
                await SendNotification(NotificationViewModelSchema(
                    Title="Security Violation",
                    Message=cust_user_profile.recent_alert_msg,
                    Phone=GetDecryptedText(cust_user_profile.mobile_number),
                    Email=GetDecryptedText(cust_user_profile.email_address),
                    Delivery_channel=notifications_sending_process
                ))
                return status
            else:  
                # OTP CHECKING
                if ConvertToBool(login_after_otp_verification):
                    status = await Authentication(CustomerOtpSchema(
                        user_id=cust_user_profile.user_id.lower(),
                        cust_id=cust_user_profile.customer_id,
                        phone_number=GetDecryptedText(cust_user_profile.mobile_number),
                        email_address=GetDecryptedText(cust_user_profile.email_address),
                        verification_channel=data.OTP_verify_channel,
                        otp=data.OTP
                    ))
                    
                    if  status.Status.upper() != "OK":
                        return status
                
                status = _IsLoginSuccess(data, cust_user_profile)
                return status
        else:
            status.Status = "FAILED"
            status.Message = "Invalid Credentials"
            status.Result = None
            AddActivityLog(SystemActivitySchema(
                Type="LOGIN",
                Title="Failed to Login",
                Details=f"{cust_user_profile.user_id.lower()} has failed to Login. Reason: {status.Message}",
                IpAddress="",
                UserType="USER",
                User_Id=cust_user_profile.user_id.lower()
            ))
        
        return status
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "LogInRoutes/Login",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        AddActivityLog(SystemActivitySchema(
            Type="LOGIN",
            Title="Failed to Login",
            Details=f"{data.UserID.lower()} has failed to Login. Reason: {status.Message}",
            IpAddress="",
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
        return status

