from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from app.core.dependencies import SessionDep, get_current_user
from app.models.chat import Chat
from app.models.user import User
from app.utils import user as user_utils
from app.schemas import chat as chat_schemas
from app.core.dependencies import UserTokenDep
from app.schemas import user as user_schemas
import json

router_chat = APIRouter(prefix="/chat", tags=["Чат"])
active_connections: List[WebSocket] = []

@router_chat.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: SessionDep, token: str):
    await websocket.accept()
    active_connections.append(websocket)
    
    current_user = await get_current_user(session, token=token)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = chat_schemas.ChatMessageCreate(
                message=data, 
                user=user_schemas.InfoUser(
                    id=current_user.id,
                    full_name=current_user.full_name,
                    role=user_schemas.Roles(current_user.role),
                    created_at=current_user.created_at,
                    avatar_image=current_user.avatar_image
                )
            )
            new_message = await Chat.create_chat_message(session, message, current_user.id)
            await broadcast(message)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast(message: chat_schemas.ChatMessageCreate):
    message_json = json.dumps({
        "message": message.message,
        "user": {
            "id": message.user.id,
            "full_name": message.user.full_name,
            "role": str(message.user.role).split(".")[1],  # Преобразуем в строку
            "created_at": message.user.created_at.isoformat() if message.user.created_at else None,  # Преобразуем в строку
            "avatar_image": message.user.avatar_image
        }
    })
    
    for connection in active_connections:
        try:
            await connection.send_text(message_json)
        except Exception as e:
            print(f"Error sending message: {e}")
            active_connections.remove(connection) 
@router_chat.get("/messages")
async def get_messages(session: SessionDep, limit: int = 150):
    messages = await Chat.get_all(session, limit)
    return messages
