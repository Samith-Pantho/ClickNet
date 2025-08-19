import hashlib
import base64
import json
import os
import random
import string
import traceback
from kafka import KafkaProducer
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from sqlalchemy import func, select
from Models.shared import customerUserProfile
from Schemas.shared import SystemLogErrorSchema, CustomerUserProfileSchema, CustomerAddMoneySchema
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from Config.dbConnection import AsyncSessionLocalClicknet
from sqlalchemy.ext.asyncio import AsyncSession

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all'
)

async def GetSha1Hash(raw_data: str) -> str:
    try:
        sha1_hash = hashlib.sha1()
        sha1_hash.update(raw_data.encode('utf-8'))
        return sha1_hash.hexdigest()
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GetSha1Hash",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def _GenerateRandomString(length: int = 32) -> str:
    try:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/_GenerateRandomString",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def _AES_Encrypt(plain_text: str, key: bytes) -> str:
    try:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Invalid AES key length: {len(key)} bytes")

        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(plain_text.encode('utf-16le'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode()
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Encrypt",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def _AES_Decrypt(encrypted_text: str, key: bytes) -> str:
    try:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Invalid AES key length: {len(key)} bytes")

        decoded = base64.b64decode(encrypted_text)
        iv = decoded[:16]
        cipher_text = decoded[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(cipher_text), AES.block_size)
        return decrypted.decode('utf-16le')
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Decrypt",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def _DeriveAESKey(key_str: str, length=32) -> bytes:
    return hashlib.sha256(key_str.encode('utf-8')).digest()[:length]

async def GetEncryptedText(plain_text: str) -> str:
    try:
        random_key_str = await _GenerateRandomString()  # e.g. 32 chars
        random_key = await _DeriveAESKey(random_key_str, 32)
        fixed_key = await _DeriveAESKey(Get("ENCRYPTION_FIXED_KEY"), 32)

        e_text = await _AES_Encrypt(plain_text, random_key)
        e_key = await _AES_Encrypt(random_key_str, fixed_key)

        return base64.b64encode((e_key + '::' + e_text).encode('utf-8')).decode('utf-8')
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GetEncryptedText",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def GetDecryptedText(encrypted_text: str) -> str | None:
    try:
        if encrypted_text:
            decoded = base64.b64decode(encrypted_text).decode('utf-8')
            e_key, e_text = decoded.split('::', 1)

            fixed_key = await _DeriveAESKey(Get("ENCRYPTION_FIXED_KEY"), 32)
            plain_random_key = await _AES_Decrypt(e_key, fixed_key)
            random_key = await _DeriveAESKey(plain_random_key, 32)

            return await _AES_Decrypt(e_text, random_key)
        return ''
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GetDecryptedText",
            CreatedBy = ""
        ))
        raise Exception(ex)
 
async def GetErrorMessage(ex:Exception):
    default_message = "Something went wrong, please try again later."
    try:
        message = str(ex)
        if hasattr(ex, 'args') and len(ex.args) > 1:
            # ex.args[1] usually holds MySQL error message
            message = ex.args[1]

        if "MySQL" in message or "SQLSTATE" in message or "pymysql" in message:
            return _GetMysqlException(message)
        else:
            return message
    except Exception as inner_ex:
        return f"{default_message} - {str(inner_ex)}"

def _GetMysqlException(msg):
    if "Insufficient Balance" in msg:
        return "Insufficient Balance."
    elif "Invalid Account" in msg:
        return "Invalid Account."
    elif "no data found" in msg or "empty result" in msg:
        return "No data found in database."
    elif "packet sequence number wrong" in msg or "Lost connection" in msg:
        return "Database connection issue. Please try again."
    elif "Data too long for column" in msg:
        return "Column size isn't sufficient in database."
    else:
        return "Exception occurred in database."

async def ConvertToBool(value):
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise ValueError("Invalid input type. Expected string.")
    
    return value.strip().lower() in ('true', '1', 'yes', 'y', 't')
    

async def SendFtNotification(addmoney:CustomerAddMoneySchema, trx_id:str) -> bool:
    db_session = None
    try:
        db_session = AsyncSessionLocalClicknet()
        result = await db_session.execute(
            select(customerUserProfile)
            .where(func.lower(customerUserProfile.c.USER_ID) == addmoney.user_id.lower())
        )
        if result is not None:
            row = result.fetchone()
        
        user_profile = CustomerUserProfileSchema(**dict(row._mapping))
        if not user_profile:
            raise ValueError("No User Information found.")
        
        is_credential_sent = False

        registered_email = (await GetDecryptedText(user_profile.email_address)).strip().lower()
        registered_mobile = (await GetDecryptedText(user_profile.mobile_number)).strip()

        SendMethod = Get("CREDENTIALS_SENDING_PROCESS")
        
        amount = str(addmoney.amount_in_cent/100)
        
        sms_body = Get(f"SMS_USER_FUND_TRANSFER_BODY")
        sms_body = sms_body.replace("_userId_", user_profile.user_id.lower()) \
                .replace("_amount_", amount) \
                .replace("_currency_", addmoney.currency.upper()) \
                .replace("_fromAccount_", addmoney.payment_via) \
                .replace("_toAccount_", addmoney.receiver_no) \
                .replace("_transactionId_", trx_id) \
                .replace("_purpose_", "Add Money")
        
        email_body = Get(f"EMAIL_USER_FUND_TRANSFER_BODY")
        email_body = email_body.replace("_userId_", user_profile.user_id.lower()) \
                .replace("_amount_", amount) \
                .replace("_currency_", addmoney.currency.upper()) \
                .replace("_fromAccount_", addmoney.payment_via) \
                .replace("_toAccount_", addmoney.receiver_no) \
                .replace("_transactionId_", trx_id) \
                .replace("_purpose_", "Add Money")   
                
        kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": SendMethod,
                    "phone": registered_mobile,
                    "email": registered_email,
                    "title": "Add Money confirmation",
                    "sms_message": sms_body,
                    "email_message": email_body
                }
            )
        try:
            kafkaAck.get(timeout=10) 
            is_credential_sent = True
        except Exception as kafka_ex:
            raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")

        return is_credential_sent
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg = error_msg,
            Type = "ERROR",
            ModuleName = "TransactionRoutes/_SendFtNotification",
            CreatedBy = ""
        ))
        return False
    finally:
        if db_session:
            await db_session.close()