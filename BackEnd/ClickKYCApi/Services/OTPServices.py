import json
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
import traceback

from kafka import KafkaProducer
from sqlalchemy import Numeric, and_, cast, func, select
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from Models.shared import customerOTP
from Schemas.shared import SystemLogErrorSchema, CustomerOtpSchema, StatusResult, VerifiyMobileRequestviewModelShema, VerifiyEmailRequestviewModelShema
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from .CommonServices import GetErrorMessage
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

customerOTPUpdater = GenericUpdater[CustomerOtpSchema, type(customerOTP)]()

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
        expiry_min = int(Get("OTP_EXPIRY_MINUTES"))
        db_session = AsyncSessionLocalClickKyc()
        
        if data.phone_otp:
            data.phone_otp_expired_at=datetime.now() + timedelta(minutes=expiry_min)
            data.phone_sent_at=datetime.now()
            data.phone_otp_remarks="PENDING"
            data.email_otp_remarks="NA"
        if data.email_otp:
            data.email_otp_expired_at=datetime.now() + timedelta(minutes=expiry_min)
            data.email_sent_at=datetime.now()
            data.phone_otp_remarks="NA"
            data.email_otp_remarks="PENDING"
            
        await GenericInserter[CustomerOtpSchema].insert_record(
            table=customerOTP,
            schema_model=CustomerOtpSchema,
            data=data,
            returning_fields=[]
        )
        
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

async def SendOTPforMobileVerification(phone_number:str) -> StatusResult:
    try:
        status = StatusResult[object]()
        isOTPsent = False
        data = CustomerOtpSchema()
        data.phone_number=phone_number
        data.phone_otp = await GenerateCode()
        
        data.phone_message = Get("SMS_VERIFICATION_BODY")
        data.phone_message = data.phone_message.replace('_code_', data.phone_otp)
        

        if await _InsertOTPIntoDB(data):
            kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": "SMS",
                    "phone": data.phone_number,
                    "email": None,
                    "title": "ClickKYC Verification",
                    "sms_message": data.phone_message,
                    "email_message": None
                }
            )
            try:
                kafkaAck.get(timeout=10) 
                isOTPsent = True
            except Exception as kafka_ex:
                raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")
            
        if isOTPsent:
            status.Status = "OTP"
            status.Message = "OTP has been sent successfully to your phone number (Whatsapp)."
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
            ModuleName = "CommonServices/SendOTPforMobileVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to send OTP. Please try again."
        status.Result = None
        return status

async def SendOTPforEmailVerification(email_address:str) -> StatusResult:
    try:
        status = StatusResult[object]()
        isOTPsent = False
        data = CustomerOtpSchema()
        data.email_address=email_address
        data.email_otp = await GenerateCode()
        
        data.email_message = Get("EMAIL_VERIFICATION_BODY")
        data.email_message = data.email_message.replace('_code_', data.email_otp)

        if await _InsertOTPIntoDB(data):
            kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": "EMAIL",
                    "phone": None,
                    "email": data.email_address,
                    "title": "ClickKYC Verification",
                    "sms_message": None,
                    "email_message": data.email_message
                }
            )
            try:
                kafkaAck.get(timeout=10) 
                isOTPsent = True
            except Exception as kafka_ex:
                raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")
            
        if isOTPsent:
            status.Status = "OTP"
            status.Message = "OTP has been sent successfully to your email."
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
            ModuleName = "CommonServices/SendOTPforEmailVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to send OTP. Please try again."
        status.Result = None
        return status
 
async def CheckMobileOTPforVerification(data: VerifiyMobileRequestviewModelShema) -> StatusResult:
    
    status = StatusResult[object]()
    db_session = None
    try:
        user_otp = CustomerOtpSchema()
        db_session = AsyncSessionLocalClickKyc()
        result = await db_session.execute(
            select(customerOTP)
            .where(
                customerOTP.c.PHONE_NUMBER == data.phone_number,
                customerOTP.c.PHONE_OTP_REMARKS == "PENDING",
                customerOTP.c.EMAIL_OTP_REMARKS == "NA"
            )
            .order_by(customerOTP.c.DB_SVR_DT.desc())
        )
        if result is not None:
            row = result.fetchone()
        
        if row:
            user_otp = CustomerOtpSchema(**dict(row._mapping))

        if user_otp:
            if datetime.now() > user_otp.phone_otp_expired_at:
                user_otp.phone_otp_remarks="EXPIRED"
                user_otp.phone_otp_verified_at=datetime.now()
                await customerOTPUpdater.update_record(
                    table=customerOTP,
                    schema_model=CustomerOtpSchema,
                    record_id=user_otp.sl,
                    update_data=user_otp,
                    id_column="SL",
                    exclude_fields={}
                )
                    
                status.Status = "FAILED"
                status.Message = "OTP has been expired"
                status.Result = None
                return status
            elif user_otp.phone_otp == data.code:
                user_otp.phone_otp_remarks="SUCCESS"
                user_otp.phone_otp_verified_at=datetime.now()
                await customerOTPUpdater.update_record(
                    table=customerOTP,
                    schema_model=CustomerOtpSchema,
                    record_id=user_otp.sl,
                    update_data=user_otp,
                    id_column="SL",
                    exclude_fields={}
                )

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
            ModuleName = "CommonServices/CheckMobileOTPforVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to verify OTP. Please try again."
        status.Result = None
        return status
    finally:
        if db_session:
            await db_session.close()

async def CheckEmailOTPforVerification(data:VerifiyEmailRequestviewModelShema) -> StatusResult:
    
    status = StatusResult[object]()
    db_session = None
    try:
        user_otp = CustomerOtpSchema()
        db_session = AsyncSessionLocalClickKyc()
        result = await db_session.execute(
            select(customerOTP)
            .where(
                customerOTP.c.EMAIL_ADDRESS == data.email_address,
                customerOTP.c.PHONE_OTP_REMARKS == "NA",
                customerOTP.c.EMAIL_OTP_REMARKS == "PENDING"
            )
            .order_by(customerOTP.c.DB_SVR_DT.desc())
        )
        if result is not None:
            row = result.fetchone()
        
        if row:
            user_otp = CustomerOtpSchema(**dict(row._mapping))

        if user_otp:
            if datetime.now() > user_otp.email_otp_expired_at:
                user_otp.email_otp_remarks="EXPIRED"
                user_otp.email_otp_verified_at=datetime.now()
                await customerOTPUpdater.update_record(
                    table=customerOTP,
                    schema_model=CustomerOtpSchema,
                    record_id=user_otp.sl,
                    update_data=user_otp,
                    id_column="SL",
                    exclude_fields={}
                )
                    
                status.Status = "FAILED"
                status.Message = "OTP has been expired"
                status.Result = None
                return status
            elif user_otp.email_otp == data.code:
                user_otp.email_otp_remarks="SUCCESS"
                user_otp.email_otp_verified_at=datetime.now()
                await customerOTPUpdater.update_record(
                    table=customerOTP,
                    schema_model=CustomerOtpSchema,
                    record_id=user_otp.sl,
                    update_data=user_otp,
                    id_column="SL",
                    exclude_fields={}
                )

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
            ModuleName = "CommonServices/CheckEmailOTPforVerification",
            CreatedBy = ""
        ))
        
        status.Status = "FAILED"
        status.Message = "Failed to verify OTP. Please try again."
        status.Result = None
        return status
    finally:
        if db_session:
            await db_session.close()
