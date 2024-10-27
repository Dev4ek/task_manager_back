from fastapi import HTTPException, status
from sqlalchemy import String, BigInteger, Sequence, DateTime, Enum, and_, delete, select, ForeignKey, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from app.core.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.schemas import user as user_schemas
from sqlalchemy.exc import IntegrityError
from uuid import UUID, uuid4

from app.schemas import user as user_schemas
from app.utils import user as user_utils
from app.schemas import chat as chat_schemas

class Chat(Base):
    __tablename__ = 'chat'
    
    uuid: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    message: Mapped[str] = mapped_column(String(312))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="chat")
    
    @staticmethod
    async def create_chat_message(session: AsyncSession, payload: chat_schemas.ChatMessageCreate, user_id) -> 'Chat':
        """
        Создание нового сообщения в чате.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            payload (task_schemas.ChatMessageCreate): Данные нового сообщения.
            user_id (int): Айди пользователя

        Returns:
            Chat: Новое созданное сообщение.
            
        """
        new_chat_message = Chat(
            message=payload.message,
            user_id=user_id,
        )
        session.add(new_chat_message)
        await session.commit()
        await session.refresh(new_chat_message)
        
        return new_chat_message

    @staticmethod
    async def get_all(session: AsyncSession, limit: int) -> List['Chat']:
        """
        Получение всех сообщений из чата.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            linit (int)
            
        Returns:
            List[Chat]: Список всех сообщений в чате.
        """
        
        stmt = (
            select(Chat)
           .options(
                selectinload(Chat.user)
           )
           .order_by(Chat.created_at.desc())
           .limit(limit)
        )
        
        result = await session.execute(stmt)
        return result.scalars().all()
        
