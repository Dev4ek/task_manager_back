from sqlalchemy import String, BigInteger, Sequence, DateTime, Enum, select
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.schemas import user as user_schemas

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
    
    role: Mapped[user_schemas.Roles] = mapped_column(Enum(user_schemas.Roles), nullable=False, default=user_schemas.Roles.GUEST)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @staticmethod
    async def signin(session: AsyncSession, payload: user_schemas.signin) -> Optional['User']:
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
