from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict
from Config.dbConnection import ws_connections

WebSocketRoutes = APIRouter()

@WebSocketRoutes.websocket("/initialize/{session_id}")
async def websocket_initialization(websocket: WebSocket, session_id: str):
    await websocket.accept()
    ws_connections[session_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections.pop(session_id, None)
