from uuid import UUID
from pydantic import BaseModel
from app.schemas import user as user_schemas


class ChatMessageCreate(BaseModel):
    message: str
    user: user_schemas.InfoUser
    
class ChatMessage(BaseModel):
    uuid: UUID
    message: str
    user: user_schemas.InfoUser