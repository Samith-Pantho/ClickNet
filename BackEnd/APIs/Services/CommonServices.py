from datetime import datetime
from email.mime.multipart import MIMEMultipart
import json
import hashlib
import base64
import random
import string
import smtplib
from pathlib import Path
from typing import Any
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from twilio.rest import Client
from email.mime.text import MIMEText
from Schemas.shared import SystemLogErrorSchema, NotificationViewModelSchema
from .LogServices import AddLogOrError
from .AppSettingsServices import FetchAppSettingsByKey

resources_path = Path(__file__).resolve().parent.parent.parent / "Resources" / "Resources.json"
g_fixed_key = FetchAppSettingsByKey("ENCRYPTION_FIXED_KEY")
twilio_account_sid = FetchAppSettingsByKey("TWILIO_ACCOUNT_SID")
twilio_auth_token = FetchAppSettingsByKey("TWILIO_AUTH_TOKEN")
twilio_mobile_number = FetchAppSettingsByKey("TWILIO_MOBILE_NUMBER")

def LoadJsonFromFile(key: str) -> Any:
    try:
        with open(resources_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        value = data.get(key)
        if value is None:  # to catch keys with falsy values like empty string or 0
            raise KeyError(f"'{key}' not found in Resources.json")
        return value
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = f"Error loading key '{key}' from JSON: {ex}",
            Type = "ERROR",
            ModuleName = "CommonServices/LoadJsonFromFile",
            CreatedBy = ""
        ))
        raise Exception(ex)

def GetSha1Hash(raw_data: str) -> str:
    try:
        sha1_hash = hashlib.sha1()
        sha1_hash.update(raw_data.encode('utf-8'))
        return sha1_hash.hexdigest()
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GetSha1Hash",
            CreatedBy = ""
        ))
        raise Exception(ex)

def _GenerateRandomString(length: int = 32) -> str:
    try:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_GenerateRandomString",
            CreatedBy = ""
        ))
        raise Exception(ex)

def _AES_Encrypt(plain_text: str, key: bytes) -> str:
    try:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Invalid AES key length: {len(key)} bytes")

        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(plain_text.encode('utf-16le'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode()
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Encrypt",
            CreatedBy = ""
        ))
        raise Exception(ex)

def _AES_Decrypt(encrypted_text: str, key: bytes) -> str:
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
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Decrypt",
            CreatedBy = ""
        ))
        raise Exception(ex)

def _DeriveAESKey(key_str: str, length=32) -> bytes:
    return hashlib.sha256(key_str.encode('utf-8')).digest()[:length]

def GetEncryptedText(plain_text: str) -> str:
    try:
        random_key_str = _GenerateRandomString()  # e.g. 32 chars
        random_key = _DeriveAESKey(random_key_str, 32)
        fixed_key = _DeriveAESKey(g_fixed_key, 32)

        e_text = _AES_Encrypt(plain_text, random_key)
        e_key = _AES_Encrypt(random_key_str, fixed_key)

        return base64.b64encode((e_key + '::' + e_text).encode('utf-8')).decode('utf-8')
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GetEncryptedText",
            CreatedBy = ""
        ))
        raise Exception(ex)

def GetDecryptedText(encrypted_text: str) -> str | None:
    try:
        if encrypted_text:
            decoded = base64.b64decode(encrypted_text).decode('utf-8')
            e_key, e_text = decoded.split('::', 1)

            fixed_key = _DeriveAESKey(g_fixed_key, 32)
            plain_random_key = _AES_Decrypt(e_key, fixed_key)
            random_key = _DeriveAESKey(plain_random_key, 32)

            return _AES_Decrypt(e_text, random_key)
        return ''
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GetDecryptedText",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def SendSMS(phone_number:str, body: str) -> bool:
    try:
       # Create a Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)

        # Send WhatsApp message
        message = client.messages.create(
            from_=f'whatsapp:{twilio_mobile_number}',
            body=f'{body}',
            to=f'whatsapp:{phone_number}'
        )
        if message.sid:
            return True
        else:
            return False     
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/SendSMS",
            
            CreatedBy = ""
        ))
        return False

async def SendEmail(email_address:str, subject:str, body: str) -> bool:
    try:
        sender_email = FetchAppSettingsByKey("CLICKNET_SENDER_EMAIL")
        password = FetchAppSettingsByKey("CLICKNET_SENDER_EMAIL_PASS")
        receiver_email = email_address

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        html_part = MIMEText(body, "html")
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        return True      
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/SendEmail",
            CreatedBy = ""
        ))
        return False
    
def GetErrorMessage(ex:Exception):
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

def ConvertToBool(value):
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise ValueError("Invalid input type. Expected string.")
    
    return value.strip().lower() in ('true', '1', 'yes', 'y', 't')

async def SendNotification(data:NotificationViewModelSchema) -> bool:
    try:
        if data.Delivery_channel.upper() == "SMS":
            return await SendSMS(data.Phone, data.Message)
        elif data.Delivery_channel.upper() == "EMAIL":
            return await SendEmail(data.Email,data.Title, data.Message)
        else:
            isSMSsent = await SendSMS(data.Phone, data.Message)
            isEmailSent = await SendEmail(data.Email,data.Title, data.Message)
            if isSMSsent or isEmailSent:
                return True
            else:
                return False
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/SendNotification",
            CreatedBy = ""
        ))
        return False