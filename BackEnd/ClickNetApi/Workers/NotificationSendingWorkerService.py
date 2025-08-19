import json
import os
import traceback
from aiokafka import AIOKafkaConsumer
from Cache.AppSettingsCache import Get
from Schemas.shared import SystemLogErrorSchema
from Services.CommonServices import ApiCall
from Services.LogServices import AddLogOrError

APIWEBHOOK_URL = os.getenv("APIWEBHOOK_URL", "http://apiwebhook:9999")

async def _SendSMS(phone_number:str, body: str) -> bool:
    try:
        payload = {
            "phone_number": phone_number,
            "body":body
        }
        headers = {
            "accept": "application/json",
            "x-api-key":  Get("API_WEBHOOK_KEY"),
            "content-type": "application/json"
        }
        
        status = await ApiCall(
            method="POST",
            url=f"{APIWEBHOOK_URL}/Webhook/SendingSMS",
            headers=headers,
            payload=payload
        )
        reply = status.get("Result")
        return reply
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "NotificationSendingWorkerService/_SendSMS",
            
            CreatedBy = ""
        ))
        return False

async def _SendEmail(email_address:str, subject:str, body: str) -> bool:
    try:
        payload = {
            "email_address": email_address,
            "subject":subject,
            "body":body
        }
        headers = {
            "accept": "application/json",
            "x-api-key":  Get("API_WEBHOOK_KEY"),
            "content-type": "application/json"
        }
        
        status = await ApiCall(
            method="POST",
            url=f"{APIWEBHOOK_URL}/Webhook/SendingEmail",
            headers=headers,
            payload=payload
        )
        reply = status.get("Result")
        return reply
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "NotificationSendingWorkerService/_SendEmail",
            CreatedBy = ""
        ))
        return False
   
async def ProcessNotification(data):
    Delivery_channel = data['delivery_channel']
    Phone = data['phone']
    Email = data['email']
    Title = data['title']
    Sms_message = data['sms_message']
    Email_message = data['email_message']

    try:
        if Delivery_channel.upper() == "SMS" and Phone:
            await _SendSMS(Phone, Sms_message)
        elif Delivery_channel.upper() == "EMAIL" and Email:
            await _SendEmail(Email, Title, Email_message)
        elif Delivery_channel.upper() == "BOTH":
            if Phone:
                await _SendSMS(Phone, Sms_message)
            if Email:
                await _SendEmail(Email, Title, Email_message)

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        print(f"NotificationSendingWorkerService Error: {error_msg}")
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="NotificationSendingWorkerService/ProcessNotification",
            CreatedBy=""
        ))

async def ConsumeNotificationRequests():
    consumer = AIOKafkaConsumer(
        'send_notification',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id="notification_consumer_group"
    )

    await consumer.start()
    try:
        async for data in consumer:
            try:
                await ProcessNotification(data.value)
            except Exception as ex:
                print(f"Error processing Kafka notification: {str(ex)}")
                continue
    finally:
        await consumer.stop()