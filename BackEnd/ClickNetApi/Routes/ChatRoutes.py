import os
import traceback
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet 
from Schemas.shared import SystemLogErrorSchema, StatusResult
from Models.shared import customerChatSessions
from Services.CommonServices import GetCurrentActiveSession, GetSha1Hash, GetErrorMessage
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from kafka import KafkaProducer
import json

ChatRoutes = APIRouter(prefix="/Chat")
producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all'
)

@ChatRoutes.post("/ChatWithAI")
async def ChatWithAI(message: Optional[str] = None, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
            
        session_id = await GetSha1Hash(session.session_id)
        
        async with AsyncSessionLocalClickNet() as session:
            # Async database operations
            result = await session.execute(
                select(customerChatSessions).where(customerChatSessions.c.SESSION_ID == session_id)
            )
            if result is not None:
                row = result.fetchone()
            if not row:
                await session.execute(
                    insert(customerChatSessions).values(
                        SESSION_ID=session_id,
                        USER_ID=currentCustuserprofile.user_id
                    )
                )
                await session.commit()
                    
        # Send to Kafka
        if message:
            kafkaAck = producer.send(
                "chat_requests",
                value={
                    "session_id": session_id,
                    "user_id": currentCustuserprofile.user_id,
                    "message": message
                }
            )
            try:
                kafkaAck.get(timeout=10) 
            except Exception as kafka_ex:
                raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")
            status.Status = "OK"
            status.Message = ""
            status.Result = session_id
        else:
            status.Status = "OK"
            status.Message = "Initialized WebSocket"
            status.Result = session_id

        return status
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ChatRoutes/ChatWithAI",
            CreatedBy=currentCustuserprofile.user_id
        ))
        status.Status = "ERROR"
        status.Message = await GetErrorMessage(ex)
        return status