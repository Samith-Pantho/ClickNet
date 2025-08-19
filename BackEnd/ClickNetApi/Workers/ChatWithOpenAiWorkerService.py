import json
import os
import traceback
from aiokafka import AIOKafkaConsumer
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import ws_connections, AsyncSessionLocalClickNet
from Schemas.shared import SystemLogErrorSchema
from Models.shared import customerChatMessages
from Services.CommonServices import ApiCall, GetTableSl
from Services.LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

APIWEBHOOK_URL = os.getenv("APIWEBHOOK_URL", "http://apiwebhook:9999")

async def ProcessMessage(data):
    session_id = data['session_id']
    user_id = data['user_id']
    message = data['message']

    try:
        messages = []
        async with AsyncSessionLocalClickNet() as session:
            # Get previous messages
            result = await session.execute(
                select(customerChatMessages.c.ROLE, customerChatMessages.c.MESSAGE)
                .where(customerChatMessages.c.SESSION_ID == session_id)
                .order_by(customerChatMessages.c.CREATED_AT)
            )
            previous = result.fetchall()

            # Build OpenAI message structure
            previous_messages = [{"role": row.ROLE.lower(), "content": row.MESSAGE} for row in previous]
            messages += previous_messages[-5:]
            messages.append({"role": "user", "content": message})
            reply = ""
            
            payload = {
                "messages": messages
            }
            headers = {
                "accept": "application/json",
                "x-api-key":  Get("API_WEBHOOK_KEY"),
                "content-type": "application/json"
            }
            
            status = await ApiCall(
                method="POST",
                url=f"{APIWEBHOOK_URL}/Webhook/GetResponseFromOpenAI",
                headers=headers,
                payload=payload
            )
            reply = status.get("Result")

            # Insert chat into DB
            await session.execute(
                insert(customerChatMessages),
                [
                    {"ID": await GetTableSl("customerChatMessages"), "SESSION_ID": session_id, "ROLE": "USER", "MESSAGE": message},
                    {"ID": await GetTableSl("customerChatMessages"), "SESSION_ID": session_id, "ROLE": "OPENAI", "MESSAGE": reply}
                ]
            )
            await session.commit()

        # Send response over websocket
        ws = ws_connections.get(session_id)
        if ws:
            payload = json.dumps({
                "ROLE": "OPENAI",
                "MESSAGE": reply
            })
            await ws.send_text(payload)

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        print(f"KafkaWorkerService Error: {error_msg}")
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ChatWithOpenAiWorkerService/ProcessMessage",
            CreatedBy=""
        ))

async def ConsumeChatRequests():
    consumer = AIOKafkaConsumer(
        'chat_requests',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id="chat_consumer_group"
    )

    await consumer.start()
    try:
        async for msg in consumer:
            try:
                await ProcessMessage(msg.value)
            except Exception as ex:
                print(f"Error processing Kafka message: {str(ex)}")
                continue
    finally:
        await consumer.stop()