import json
import hashlib
import base64
import os
import random
import string
from pathlib import Path
import traceback
from typing import Any, Dict, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from fastapi import HTTPException
import httpx
from kafka import KafkaProducer
from sqlalchemy import and_, desc, func, select
from cryptography.fernet import Fernet
from Models.shared import customerSession
from Schemas.shared import SystemLogErrorSchema, NotificationViewModelSchema, CustomoerSessionSchema, CustomerUserProfileSchema, StatusResult
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from .CallClickNetSPServices import sp_get_table_sl
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

resources_path = Path(__file__).resolve().parent.parent / "Resources" / "Resources.json"

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all'
)

async def LoadJsonFromFile(key: str) -> Any:
    try:
        with open(resources_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        value = data.get(key)
        if value is None:  # to catch keys with falsy values like empty string or 0
            raise KeyError(f"'{key}' not found in Resources.json")
        return value
    except Exception as ex:
        await AddLogOrError(SystemLogErrorSchema(
            Msg = f"Error loading key '{key}' from JSON: {ex}",
            Type = "ERROR",
            ModuleName = "CommonServices/LoadJsonFromFile",
            CreatedBy = ""
        ))
        raise Exception(ex)

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

async def SendNotification(data:NotificationViewModelSchema) -> bool:
    try:
        kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": data.Delivery_channel,
                    "phone": data.Phone,
                    "email": data.Email,
                    "Title": data.Title,
                    "sms_message": data.Message,
                    "email_message": data.Message,
                }
            )
        try:
            kafkaAck.get(timeout=10) 
        except Exception as kafka_ex:
            raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")
        return True
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/SendNotification",
            CreatedBy = ""
        ))
        return False
    
async def GetCurrentActiveSession(user_id:str) -> CustomoerSessionSchema :
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
            select(customerSession)
            .where(
                and_(
                    func.lower(customerSession.c.USER_ID) == func.lower(user_id),
                    customerSession.c.ACTIVE_FLAG == 1,
                    customerSession.c.STATUS == 1
                )
            )
            .order_by(desc(customerSession.c.START_TIME)) 
            .limit(1)
        )
        if result is not None:
            row = result.fetchone()
        if row:
            return CustomoerSessionSchema(**dict(row._mapping))
        else:
            return None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GetCurrentActiveSession",
            CreatedBy = ""
        ))
        return None
    
    finally:
        if db_session:
            await db_session.close()
    
async def SendCredentials(data:CustomerUserProfileSchema, type:str, new_password:Optional[str]) -> StatusResult:
    status = StatusResult()
    try:
        is_credential_sent = False

        if not type:
            raise ValueError("Missing criteria for sending credentials.")
        
        registered_email = (await GetDecryptedText(data.email_address)).strip().lower()
        registered_mobile = (await GetDecryptedText(data.mobile_number)).strip()
        
        SendMethod = Get("CREDENTIALS_SENDING_PROCESS")
        
        sms_body = Get(f"SMS_USER_{type.upper()}_BODY")
        sms_body = sms_body.replace("_userId_", data.user_id.lower())
        if new_password:
            sms_body = sms_body.replace("_password_", new_password)
            
        email_body = Get(f"EMAIL_USER_{type.upper()}_BODY")
        email_body = email_body.replace("_userId_", data.user_id.lower())
        if new_password:
            email_body = email_body.replace("_password_", new_password)
        
        kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": SendMethod,
                    "phone": registered_mobile,
                    "email": registered_email,
                    "title": "ClickNet Credentials",
                    "sms_message": sms_body,
                    "email_message": email_body
                }
            )
        try:
            kafkaAck.get(timeout=10) 
            is_credential_sent = True
        except Exception as kafka_ex:
            raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")

        if is_credential_sent:
            status.Status = "OK"
            if SendMethod == "SMS":
                status.Message = "Credentials are changed successfully. Please Check your SMS for Login Credentials."
            elif SendMethod == "EMAIL":
                status.Message = "Credentials are changed successfully. Please Check your Mail for Login Credentials."
            else:
                status.Message = "Credentials are changed successfully. Please Check your Mail/SMS for Login Credentials."
            status.Result = None
            
        else:
            status.Status = "FAILED"
            if SendMethod == "SMS":
                status.Message = f"Could not send Credentials to {registered_mobile}" if registered_mobile else "Could not send Credentials"
            elif SendMethod == "EMAIL":
                status.Message = f"Could not send Credentials to {registered_email}" if registered_email else "Could not send Credentials"
            elif SendMethod == "BOTH":
                if registered_email and registered_mobile:
                    status.Message = f"Could not send Credentials to {registered_email} or {registered_mobile}"
                elif registered_mobile:
                    status.Message = f"Could not send Credentials to {registered_mobile}"
                elif registered_email:
                    status.Message = f"Could not send Credentials to {registered_email}"
                else:
                    status.Message = "Could not send Credentials"
            status.Result = None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/SendCredentials",
            CreatedBy = ""
        ))
    return status

async def EncryptImage(image_bytes: bytes) -> bytes:
    fernet = Fernet(Get("FERNET_SECRET_KEY"))
    return fernet.encrypt(image_bytes)

async def DecryptImage(encrypted_bytes: bytes) -> bytes:
    fernet = Fernet(Get("FERNET_SECRET_KEY"))
    return fernet.decrypt(encrypted_bytes)

async def GetTableSl(tableNm:str):
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        return await sp_get_table_sl(db_session, tableNm)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CommonServices/GetTableSl",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()


async def ApiCall(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {str(e)}\n{traceback.format_exc()}"
            await AddLogOrError(SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="CommonServices/ApiCall",
                CreatedBy=""
            ))
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"External API error: {str(e)}"
            )
            
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}\n{traceback.format_exc()}"
            await AddLogOrError(SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="CommonServices/ApiCall",
                CreatedBy=""
            ))
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
            await AddLogOrError(SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="CommonServices/ApiCall",
                CreatedBy=""
            ))
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
