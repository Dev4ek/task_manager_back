from fastapi import HTTPException, status
from sqlalchemy import String, BigInteger, Sequence, DateTime, Enum, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.schemas import user as user_schemas
from sqlalchemy.exc import IntegrityError

from app.schemas import user as user_schemas
from app.utils import user as user_utils

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence('user_id_seq_rand', start=115321, increment=3), 
        primary_key=True,
        index=True
    )
    full_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    login: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(200))
    
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    avatar_image: Mapped[str] = mapped_column(String(300), default="static/avatars/default.jpeg")
    
    role: Mapped[user_schemas.Roles] = mapped_column(Enum(user_schemas.Roles), nullable=False, default=user_schemas.Roles.GUEST)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    tasks = relationship("Task", back_populates="user")
    chat = relationship("Chat", back_populates="user")

    @staticmethod
    async def signin(session: AsyncSession, payload: user_schemas.Signin) -> Optional['User']:
        """
        Авторизация пользователя, проверяя предоставленный логин и пароль.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            login (str): Логин пользователя.
            password (str): Пароль пользователя.

        Returns:
            Optional[User]: Объект пользователя, если аутентификация успешна, иначе None.
        """
        stmt = select(User).filter(User.login == payload.login)
        result = await session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()

        if user and await user_utils.check_password(payload.password, user.password):
            return user
        return None

    @staticmethod
    async def check_login(session: AsyncSession, login: str) -> bool:
        """
        Проверяет, существует ли уже такой логин в системе.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            login (str): Логин для проверки.

        Returns:
            bool: True, если логин существует, False в противном случае.
        """
        stmt = select(User).filter(User.login == login)
        result = await session.execute(stmt)
        existing_user = result.first()

        return existing_user is not None

    @staticmethod
    async def signup(session: AsyncSession, payload: user_schemas.Signup) -> Optional['User']:
        """
        Регистрация пользователя, добавляя его в базу данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            payload (user_schemas.Signup): Данные для регистрации.

        Returns:
            Optional[User]: Объект пользователя, если регистрация успешна, иначе None.
        """
        hashed_password = await user_utils.hash_password(payload.password)

        new_user = User(
            full_name=payload.full_name,
            login=payload.login,
            password=hashed_password
        )

        session.add(new_user)
        try:
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError:
            await session.rollback()
            raise 
        
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional['User']:
        """
        Получение пользователя по его идентификатору.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            user_id (int): Идентификатор пользователя.
            
        Returns:
            Optional[User]: Объект пользователя, если найден, иначе None.
        """
        stmt = select(User).filter(User.id == user_id)
        result = await session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()
        return user
    
    @staticmethod
    async def get_all_users(session: AsyncSession):
        """
        Получение всех пользователей из базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            
        Returns:
            List[User]: Список всех пользователей.
        """
        stmt = select(User)
        result = await session.execute(stmt)
        return result.scalars().all()