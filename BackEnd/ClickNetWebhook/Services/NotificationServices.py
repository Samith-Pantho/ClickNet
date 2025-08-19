from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import traceback
from typing import Any, Dict
from twilio.rest import Client
from Schemas.shared import SystemLogErrorSchema
from Services.LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

async def SendSMS(data: Dict[str, Any]) -> bool:
    try:
        twilio_account_sid = Get("TWILIO_ACCOUNT_SID")
        twilio_auth_token = Get("TWILIO_AUTH_TOKEN")
        twilio_mobile_number = Get("TWILIO_MOBILE_NUMBER")
       # Create a Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)

        # Send WhatsApp message
        message = client.messages.create(
            from_=f'whatsapp:{twilio_mobile_number}',
            body=f'{data.get("body")}',
            to=f'whatsapp:{data.get("phone_number")}'
        )
        if message.sid:
            return True
        else:
            raise ValueError(message)    
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "NotificationSendingWorkerService/_SendSMS",
            CreatedBy = ""
        ))
        return False

async def SendEmail(data: Dict[str, Any]) -> bool:
    try:
        sender_email = Get("CLICKNET_SENDER_EMAIL")
        password = Get("CLICKNET_SENDER_EMAIL_PASS")
        receiver_email = data.get("email_address")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = data.get("subject")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        html_part = MIMEText(data.get("body"), "html")
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        return True      
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "NotificationSendingWorkerService/_SendEmail",
            CreatedBy = ""
        ))
        return False