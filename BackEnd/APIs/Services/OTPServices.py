import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import Numeric, and_, cast, func
from Config.dbConnection import conn, engine 
from Models.shared import customerOTP
from Schemas.shared import SystemLogErrorSchema, CustomerOtpSchema, StatusResult
from .CommonServices import GetErrorMessage, SendEmail, SendSMS
from .LogServices import AddLogOrError
from .AppSettingsServices import FetchAppSettingsByKey
from .CallClickNetSPServices import sp_get_pending_otp

dev_mode = FetchAppSettingsByKey("APPLICATION_DEVELOPMENT_MODE")
otp_type = FetchAppSettingsByKey("OTP_TYPE")
otp_length = int(FetchAppSettingsByKey("OTP_LENGTH") or "6")
sms_verification_body = FetchAppSettingsByKey("SMS_VERIFICATION_BODY")
email_verification_body = FetchAppSettingsByKey("EMAIL_VERIFICATION_BODY")
otp_expiry_minutes = int(FetchAppSettingsByKey("OTP_EXPIRY_MINUTES"))

def _GenerateOTP(otp_length: int, otp_type: str, sequential_call: bool) -> str:
    try:
        otp_type = otp_type.upper()
        combination = ""

        if otp_type == "NUMARIC":
            if sequential_call:
                combination = "987654321"
            else:
                combination = "123456789"
        elif otp_type == "ALPHA_NUMARIC":
            if sequential_call:
                combination = "abcdefghjmnpqrstuvwxyz123456789ABCDEFGHJLMNPQRSTUVWXY"
            else:
                combination = "ABCDEFGHJLMNPQRSTUVWXYZ123456789abcdefghjmnpqrstuvwxyz"
        elif otp_type == "NON_ALPHA_NUMARIC":
            if sequential_call:
                combination = "!@#$%^&*|abcdefghjmnpqrstuvwxyz23456789ABCDEFGHJLMNPQRSTUVWXY"
            else:
                combination = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789!@#$%^&*|"
        else:
            # default case
            if sequential_call:
                combination = "987654321"
            else:
                combination = "123456789"

        try:
            return ''.join(random.choice(combination) for _ in range(otp_length))
        except Exception as ex:
            raise Exception(f"OTP Generation failed! {ex}")
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_GenerateOTP",
            CreatedBy = ""
        ))
        raise Exception(ex)
    
def GenerateCode():
    try:
        # Development mode: always return "123456"
        if str(dev_mode).lower() == "true":
                return "123456"
        else:
            plain_otp = _GenerateOTP(otp_length, otp_type, True)
            return plain_otp
    
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GenerateCode",
            CreatedBy = ""
        ))
        return None

async def _SendOTPForMobileVerification(data:CustomerOtpSchema) -> bool:
    try:
        if data.phone_number:
            data.message = sms_verification_body.replace('_code_', data.otp)
            if _InsertOTPIntoDB(data):
                return await SendSMS(data.phone_number, data.message)
            else:
                return False
        else:
            return False
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_SendOTPForMobileVerification",
            CreatedBy = ""
        ))
        return False
    
async def _SendOTPForEmailVerification(data:CustomerOtpSchema) -> bool:
    try:
        if data.email_address:
            data.message = email_verification_body.replace('_code_', data.otp)
            if _InsertOTPIntoDB(data):
                return await SendEmail(data.email_address, "ClickNet Verification", data.message)
            else:
                return False
        else:
            return False
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_SendOTPForEmailVerification",
            CreatedBy = ""
        ))
        return False
    
async def _SendOTPForMobileAndEmailVerification(data:CustomerOtpSchema) -> bool:
    try:
        sms_message = ""
        email_message = ""
        is_sms_message_sent = False
        is_email_message_sent = False

        if data.phone_number:
            sms_message = sms_verification_body.replace('_code_', data.otp)
        if data.email_address:
            email_message = sms_verification_body.replace('_code_', data.otp)

        data.message = sms_message
        if sms_message and email_message:
            data.message += "\n"
            data.message += email_message
        
        if _InsertOTPIntoDB(data):
            if data.phone_number:
                is_sms_message_sent = await SendSMS(data.phone_number, sms_message)
            if data.email_address:
                is_email_message_sent = await SendEmail(data.email_address, "ClickNet Verification", email_message)
            
            if is_sms_message_sent or is_email_message_sent:
                return True
            else:
                return False
        else:
            return False
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_SendOTPForMobileAndEmailVerification",
            CreatedBy = ""
        ))
        return False
    
def _InsertOTPIntoDB(data:CustomerOtpSchema) -> bool:
    try:
        new_otp = customerOTP.insert().values(
            USER_ID=data.user_id.lower(),
            CUST_ID=data.cust_id,
            PHONE_NUMBER=data.phone_number,
            EMAIL_ADDRESS=data.email_address,
            VERIFICATION_CHANNEL=data.verification_channel,
            MESSAGE=data.message,
            OTP=data.otp,
            OTP_EXPIRED_AT=datetime.now() + timedelta(minutes=otp_expiry_minutes),
            OTP_VERIFIED_AT=None,
            SENT_AT=None,
            FROM_ACCOUNT_NO=data.from_account_no,
            FROM_BRANCH_ID=data.from_branch_id,
            TO_ACCOUNT_NO=data.to_account_no,
            TO_BRANCH_ID=data.to_branch_id,
            TO_BANK_ID=data.to_bank_id,
            TO_ROUTING_NUMB=data.to_routing_numb,
            IP_ADDRESS=data.ip_address,
            AMOUNT_CCY=data.amount_ccy if data.amount_ccy is not None else Decimal("0.0"),
            AMOUNT_LCY=data.amount_lcy if data.amount_lcy is not None else Decimal("0.0"),
            TRANSFER_TYPE=data.transfer_type,
            RECEIVER_ID=data.receiver_id,
            PURPOSE_OF_TRANSACTION=data.purpose_of_transaction,
            RECEIVER_NM=data.receiver_nm,
            REMARKS="PENDING"
        )
        
        with engine.begin() as _conn:
            _conn.execute(new_otp)
        
        return True
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_InsertOTPIntoDB",
            CreatedBy = ""
        ))
        return False

async def SendOTPforVerification(data:CustomerOtpSchema) -> StatusResult:
    try:
        status = StatusResult[object]()
        data.otp = GenerateCode()
        
        isOTPsent = False
        
        if data.verification_channel.upper() == "SMS":
            isOTPsent = await _SendOTPForMobileVerification(data)
            if isOTPsent:
                status.Status = "OTP"
                status.Message = "OTP has been sent successfully to your registered phone number (Whatsapp)."
                status.Result = None
                return status
        elif data.verification_channel.upper() == "EMAIL":
            isOTPsent = await _SendOTPForEmailVerification(data)
            if isOTPsent:
                status.Status = "OTP"
                status.Message = "OTP has been sent successfully to your registered Email."
                status.Result = None
                return status
        elif data.verification_channel.upper() == "BOTH":
            isOTPsent = await _SendOTPForMobileAndEmailVerification(data)
            if isOTPsent:
                status.Status = "OTP"
                status.Message = "OTP has been sent successfully to your registered phone number (Whatsapp) or email."
                status.Result = None
                return status    
        
        status.Status = "FAILED"
        status.Message = "Failed to send OTP. Please try again."
        status.Result = None
        return status        
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/SendOTPforVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to send OTP. Please try again."
        status.Result = None
        return status
 
async def CheckOTPforVerification(data:CustomerOtpSchema) -> StatusResult:
    
    status = StatusResult[object]()
    try:
        now = datetime.utcnow()
        cutofftime = now - timedelta(minutes=otp_expiry_minutes)
        with engine.connect() as _conn:
            user_otp = sp_get_pending_otp(_conn, data, cutofftime)

        if user_otp:
            if datetime.now() > user_otp.otp_expired_at:
                with engine.begin() as _conn:
                    _conn.execute(customerOTP.update().values(REMARKS="EXPIRED").where(customerOTP.c.OTP_SL == user_otp.otp_sl))
                    
                status.Status = "FAILED"
                status.Message = "OTP has been expired"
                status.Result = None
                return status
            elif user_otp.otp == data.otp:
                # Update OTP_VERIFIED_AT to now
                with engine.begin() as _conn:
                    _conn.execute(customerOTP.update().values(OTP_VERIFIED_AT=datetime.now(), REMARKS="SUCCESS" ).where(customerOTP.c.OTP_SL == user_otp.otp_sl))

                status.Status = "OK"
                status.Message = "OTP Verification Successful."
                status.Result = None
                return status
            else:
                status.Status = "FAILED"
                status.Message = "Wrong OTP."
                status.Result = None
                return status
        else:
            status.Status = "FAILED"
            status.Message = "OTP Verification Failed."
            status.Result = None
            return status
    except Exception  as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/CheckOTPforVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to verify OTP. Please try again."
        status.Result = None
        return status

async def Authentication(data: CustomerOtpSchema) -> StatusResult:
    status = StatusResult[object]()
    try:
        if data.otp == "":
            status = await SendOTPforVerification(data)
        else:
            status = await CheckOTPforVerification(data)
        return status
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/Authentication",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = GetErrorMessage(ex)
        status.Result = None
        return status