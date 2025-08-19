import json
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
import traceback

from kafka import KafkaProducer
from sqlalchemy import Numeric, and_, cast, func
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from Models.shared import customerOTP
from Schemas.shared import SystemLogErrorSchema, CustomerOtpSchema, StatusResult
from .CommonServices import GetErrorMessage, GetTableSl
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from .CallClickNetSPServices import sp_get_pending_otp

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all'
)

async def _GenerateOTP(sequential_call: bool) -> str:
    try:
        otp_type = Get("OTP_TYPE").upper()
        combination = ""

        if otp_type == "NUMARIC":
            if sequential_call:
                combination = "987654321"
            else:
                combination = "123456789"
        elif otp_type == "ALPHA_NUMARIC":
            if sequential_call:
                combination = "abcasync def ghjmnpqrstuvwxyz123456789ABCasync def GHJLMNPQRSTUVWXY"
            else:
                combination = "ABCasync def GHJLMNPQRSTUVWXYZ123456789abcasync def ghjmnpqrstuvwxyz"
        elif otp_type == "NON_ALPHA_NUMARIC":
            if sequential_call:
                combination = "!@#$%^&*|abcasync def ghjmnpqrstuvwxyz23456789ABCasync def GHJLMNPQRSTUVWXY"
            else:
                combination = "abcasync def ghijkmnpqrstuvwxyzABCasync def GHJKLMNPQRSTUVWXYZ123456789!@#$%^&*|"
        else:
            # async def ault case
            if sequential_call:
                combination = "987654321"
            else:
                combination = "123456789"

        try:
            return ''.join(random.choice(combination) for _ in range(int(Get("OTP_LENGTH"))))
        except Exception as ex:
            raise Exception(f"OTP Generation failed! {ex}")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/_GenerateOTP",
            CreatedBy = ""
        ))
        raise Exception(ex)
    
async def GenerateCode():
    try:
        dev_mode = Get("APPLICATION_DEVELOPMENT_MODE")
        # Development mode: always return "123456"
        if str(dev_mode).lower() == "true":
                return "123456"
        else:
            plain_otp = await _GenerateOTP(True)
            return plain_otp
    
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GenerateCode",
            CreatedBy = ""
        ))
        return None
    
async def _InsertOTPIntoDB(data:CustomerOtpSchema) -> bool:
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        new_otp = customerOTP.insert().values(
            OTP_SL= await GetTableSl("customerOTP"),
            USER_ID=data.user_id.lower(),
            CUST_ID=data.cust_id,
            PHONE_NUMBER=data.phone_number,
            EMAIL_ADDRESS=data.email_address,
            VERIFICATION_CHANNEL=data.verification_channel,
            MESSAGE=data.message,
            OTP=data.otp,
            OTP_EXPIRED_AT=datetime.now() + timedelta(minutes=int(Get("OTP_EXPIRY_MINUTES"))),
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
        
        await db_session.execute(new_otp)
        await db_session.commit()
        
        return True
    except Exception  as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/_InsertOTPIntoDB",
            CreatedBy = ""
        ))
        return False
    finally:
        if db_session:
            await db_session.close()

async def SendOTPforVerification(data:CustomerOtpSchema) -> StatusResult:
    try:
        status = StatusResult[object]()
        isOTPsent = False
        data.otp = await GenerateCode()
        
        isOTPsent = False
        sms_body = Get("SMS_VERIFICATION_BODY")
        sms_body = sms_body.replace('_code_', data.otp)
        
        email_body = Get("EMAIL_VERIFICATION_BODY")
        email_body = email_body.replace('_code_', data.otp)

        if await _InsertOTPIntoDB(data):
            kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": data.verification_channel.upper(),
                    "phone": data.phone_number,
                    "email": data.email_address,
                    "title": "ClickNet Verification",
                    "sms_message": sms_body,
                    "email_message": email_body
                }
            )
            try:
                kafkaAck.get(timeout=10) 
                isOTPsent = True
            except Exception as kafka_ex:
                raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")
            
        if isOTPsent:
            status.Status = "OTP"
            status.Message = "OTP has been sent successfully to your registered phone number (Whatsapp)."
            status.Result = None
        else:
            status.Status = "FAILED"
            status.Message = "Failed to send OTP. Please try again."
            status.Result = None
        return status        
    except Exception  as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
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
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        now = datetime.now()
        cutofftime = now - timedelta(minutes=int(Get("OTP_EXPIRY_MINUTES")))
        user_otp = await sp_get_pending_otp(db_session, data, cutofftime)

        if user_otp:
            if datetime.now() > user_otp.otp_expired_at:
                await db_session.execute(customerOTP.update().values(REMARKS="EXPIRED").where(customerOTP.c.OTP_SL == user_otp.otp_sl))
                await db_session.commit()
                    
                status.Status = "FAILED"
                status.Message = "OTP has been expired"
                status.Result = None
                return status
            elif user_otp.otp == data.otp:
                # Update OTP_VERIFIED_AT to now
                await db_session.execute(customerOTP.update().values(OTP_VERIFIED_AT=datetime.now(), REMARKS="SUCCESS" ).where(customerOTP.c.OTP_SL == user_otp.otp_sl))
                await db_session.commit()

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
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/CheckOTPforVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to verify OTP. Please try again."
        status.Result = None
        return status
    finally:
        if db_session:
            await db_session.close()

async def Authentication(data: CustomerOtpSchema) -> StatusResult:
    status = StatusResult[object]()
    try:
        if data.otp == "":
            status = await SendOTPforVerification(data)
        else:
            status = await CheckOTPforVerification(data)
        return status
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/Authentication",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        return status