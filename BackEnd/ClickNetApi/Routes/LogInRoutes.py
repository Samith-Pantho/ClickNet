import traceback
from typing import Optional
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet
from Models.shared import customerUserProfile, customerSession, systemAdvertisements
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema, LoginViewModelSchema, CustomerUserProfileSchema, CustomoerSessionSchema, NotificationViewModelSchema, CustomerOtpSchema, SystemAdvertisementsSchema, SystemCaptchaLogSchema
from Services.ActivityServices import AddActivityLog
from Services.CaptchaService import VerifyCaptchaToken, DisableCaptchaToken
from Services.JWTTokenServices import GenerateJWTToken
from Services.LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from Services.CommonServices import GetSha1Hash, GetDecryptedText, ConvertToBool, SendNotification, GetErrorMessage
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.OTPServices import Authentication

customerUserProfileUpdater = GenericUpdater[CustomerUserProfileSchema, type(customerUserProfile)]()
customerSessionUpdater = GenericUpdater[CustomoerSessionSchema, type(customerSession)]()

LogInRoutes = APIRouter(prefix="/Login")

async def _CheckLoginCredentials(data: LoginViewModelSchema) -> Optional[CustomerUserProfileSchema]:
    db_session = None
    try:
        user_profile = CustomerUserProfileSchema()
        
        if data:
            db_session = AsyncSessionLocalClickNet()
            result = await db_session.execute(
                select(customerUserProfile)
                .where(func.lower(customerUserProfile.c.USER_ID) == data.UserID.lower())
            )
            if result is not None:
                row = result.fetchone()
            
            if row:
                user_profile = CustomerUserProfileSchema(**dict(row._mapping))
            
            if user_profile:
                if user_profile.password_string:
                    if await GetSha1Hash(data.Password) == user_profile.password_string:
                        
                        if not user_profile.user_profile_closed_flag:
                            if not user_profile.locked_flag:
                                if user_profile.user_status_active_flag:
                                    user_profile.recent_alert_msg = ""
                                    user_profile.failed_login_attempts_nos = 0
                                    user_profile.failed_pasword_recovery_attempts_nos = 0
                                    user_profile.failed_userid_recovery_attempts_nos = 0
                                    
                                    if user_profile.last_password_changed_on:
                                        password_expiry_date = user_profile.last_password_changed_on + timedelta(days=int(Get("PASSWORD_EXPIRY_DAYS")))
                                    
                                        if datetime.now() > password_expiry_date:
                                            user_profile.force_password_changed_flag = True
                                    else:
                                        user_profile.last_password_changed_on = user_profile.last_signed_on
                                    
                                    user_profile.last_signed_on = datetime.now()
                                    
                                    return await customerUserProfileUpdater.update_record(
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
                        login_wrong_attempts_limit = Get("LOGIN_WRONG_PASSWORD_ATTEMPT_LIMIT")
                        if user_profile.failed_login_attempts_nos < int(login_wrong_attempts_limit):
                            user_profile.failed_login_attempts_nos += 1
                            user_profile.recent_alert_msg = f"Wrong Password attempt {user_profile.failed_login_attempts_nos} times."
                        
                        if user_profile.failed_login_attempts_nos == int(login_wrong_attempts_limit):
                            user_profile.recent_alert_msg = (
                                f"Your account has been deactivated due to {int(login_wrong_attempts_limit)} times wrong attempts."
                            )
                            user_profile.user_status_active_flag = False
                            user_profile.force_password_changed_flag = True
            else:
                return None
        
        return await customerUserProfileUpdater.update_record(
            table=customerUserProfile,
            schema_model=CustomerUserProfileSchema,
            record_id=user_profile.user_id,
            update_data=user_profile,
            id_column="USER_ID",
            exclude_fields={}
        )
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="LogInRoutes/_CheckLoginCredentials",
            CreatedBy=""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def _create_session(access_token: str) -> bool:
    db_session = None
    try:
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        user_id = await GetDecryptedText(decoded_token.get("UserId"))
        session_id = await GetDecryptedText(decoded_token.get("SessionID"))
        ip_Address = decoded_token.get("IpAddress")
        
        # Clear Previous User Session
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
            select(customerSession)
            .where(
                and_(
                    func.lower(customerSession.c.USER_ID) == func.lower(user_id),
                    customerSession.c.ACTIVE_FLAG == 1
                )
            )
        )
        rows = result.fetchall()
        previous_user_list = [CustomoerSessionSchema(**dict(row._mapping)) for row in rows]
        
        if previous_user_list:
            for user_session in previous_user_list:
                user_session.active_flag = 0
                user_session.status = 0
                user_session.remarks = f"Logged out from {user_session.ip_address} by Application. Reason: session expired."
                await customerSessionUpdater.update_record(
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
            await GenericInserter[CustomoerSessionSchema].insert_record(
                table=customerSession,
                schema_model=CustomoerSessionSchema,
                data=new_session,
                returning_fields=[]
            )
            return True
        except Exception as ex:
            error_msg = f"{str(ex)}\n{traceback.format_exc()}"
            await AddLogOrError(SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="LogInRoutes/_create_session",
                CreatedBy=""
            ))
            return False
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="LogInRoutes/_create_session",
            CreatedBy=""
        ))
        return False
    finally:
        if db_session:
            await db_session.close()

async def _IsLoginSuccess(data: LoginViewModelSchema, cust_user_profile: CustomerUserProfileSchema) -> StatusResult:
    status = StatusResult()
    # Generate Token, Create Session for SuccessFull login
    access_token = await GenerateJWTToken(cust_user_profile.user_id, data.IPAddress)
    
    if access_token and await _create_session(access_token):
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        start_date = decoded_token.get("StartDate")
        expiry_date = decoded_token.get("ExpiryDate")
        
        db_session = None
        try:
            db_session = AsyncSessionLocalClickNet()
            result = await db_session.execute(
                select(systemAdvertisements)
                .where(systemAdvertisements.c.STATUS == 1)
            )
            rows = result.fetchall()
            advertisements = [SystemAdvertisementsSchema(**dict(row._mapping)) for row in rows]
            
            login_response_model = {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int((datetime.fromisoformat(expiry_date) - datetime.fromisoformat(start_date)).total_seconds() * 1000),
                "userName": cust_user_profile.user_id,
                "fullName": cust_user_profile.user_nm,
                "issued": start_date,
                "expires": expiry_date,
                "customerId": cust_user_profile.customer_id,
                "ForcePasswordChangedFlag": cust_user_profile.force_password_changed_flag,
                "Advertisements": advertisements
            }
            
            status.Status = "OK"
            status.Message = "Successfully logged in"
            status.Result = login_response_model
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.LOGIN,
                Title="Successfully logged in",
                Details=f"{cust_user_profile.user_id.lower()} is successfully logged in.",
                IpAddress=data.IPAddress,
                UserType="USER",
                User_Id=cust_user_profile.user_id.lower()
            ))
        except Exception as ex:
            status.Status = "FAILED"
            status.Message = "Failed to fetch advertisements"
            status.Result = None
        finally:
            if db_session:
                await db_session.close()
    else:
        status.Status = "FAILED"
        status.Message = "Failed to create access token"
        status.Result = None
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.LOGIN,
            Title="Failed to Login",
            Details=f"{cust_user_profile.user_id.lower()} has failed to Login. Reason: {status.Message}",
            IpAddress=data.IPAddress,
            UserType="USER",
            User_Id=cust_user_profile.user_id.lower()
        ))
    
    return status

@LogInRoutes.post("/Login")
async def Login(data: LoginViewModelSchema) -> StatusResult:
    status = StatusResult()
    cust_user_profile = CustomerUserProfileSchema()
    
    try:
        isHuman = await VerifyCaptchaToken(data.captcha_token)
        if not isHuman:
            raise ValueError("CAPTCHA verification failed.")
    
        if await ConvertToBool(Get("SYSTEM_DOWN")):
            raise ValueError(Get("SYSTEM_DOWN_MSG"))
        
        # Licence Checking
        if await ConvertToBool(Get("ENABLE_LICENCE_CHECKING")):
            license_checking_msg = "" 
            if license_checking_msg:
                raise ValueError(f"Licence Error: {license_checking_msg}")
            
        # Check user in DB
        cust_user_profile = await _CheckLoginCredentials(data)
        
        if cust_user_profile:
            if cust_user_profile.recent_alert_msg:
                await SendNotification(NotificationViewModelSchema(
                    Title="Security Violation",
                    Message=cust_user_profile.recent_alert_msg,
                    Phone=await GetDecryptedText(cust_user_profile.mobile_number),
                    Email=await GetDecryptedText(cust_user_profile.email_address),
                    Delivery_channel=Get("NOTIFICATIONS_SENDING_PROCESS").upper()
                ))
                raise ValueError(cust_user_profile.recent_alert_msg)
            else:  
                # OTP CHECKING
                if await ConvertToBool(Get("LOGIN_AFTER_OTP_VERIFICATION")):
                    status = await Authentication(CustomerOtpSchema(
                        user_id=cust_user_profile.user_id.lower(),
                        cust_id=cust_user_profile.customer_id,
                        phone_number=await GetDecryptedText(cust_user_profile.mobile_number),
                        email_address=await GetDecryptedText(cust_user_profile.email_address),
                        verification_channel=data.OTP_verify_channel,
                        otp=data.OTP
                    ))
                    
                    if status.Status.upper() != "OK":
                        return status
                
                status = await _IsLoginSuccess(data, cust_user_profile)
        else:
            raise ValueError("Invalid Credentials")
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="LogInRoutes/Login",
            CreatedBy=""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.LOGIN,
            Title="Failed to Login",
            Details=f"{data.UserID.lower()} has failed to Login. Reason: {status.Message}",
            IpAddress=data.IPAddress,
            UserType="USER",
            User_Id=data.UserID.lower()
        ))
    await DisableCaptchaToken(data.captcha_token)
    return status