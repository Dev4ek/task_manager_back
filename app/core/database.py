import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, insert, create_engine
from app.utils import user as user_utils
from app.models.user import User
from .config import settings
from .base import Base


engine = create_async_engine(url=settings.SQLALCHEMY_DATABASE_URL)
engine_sync = create_engine(url=settings.SQLALCHEMY_DATABASE_SYNC_URL)


async def get_session():
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()

def create_tables():
    # Base.metadata.drop_all(engine_sync, checkfirst=True)
    # search_utils.delete_index("products")
    # search_utils.create_index("products")
    Base.metadata.create_all(engine_sync, checkfirst=True)
    ...
    

def create_test_user():
    with engine_sync.connect() as conn:
        result = conn.execute(
            select(User)
            .filter(User.login == 'admin')
        ).first()
        
        if result is None:  # user not exist
            # Вызов асинхронной функции в синхронном коде
            hashed_password = asyncio.run(user_utils.hash_password('admin'))
            
            conn.execute(
                insert(User).values(
                    full_name="Админ фио лучший",
                    login='admin',
                    password=hashed_password,
                    role='ADMIN'
                )
            )
            conn.commit()  # Commit the transacti
            
            hashed_password = asyncio.run(user_utils.hash_password('guest'))
            
            conn.execute(
                insert(User).values(
                    full_name="Гость фио крутой",
                    login='guest',
                    password=hashed_password,
                    role='GUEST'
                )
            )
            conn.commit()  # Commit the transacti
            
        
            hashed_password = asyncio.run(user_utils.hash_password('member'))
            
            conn.execute(
                insert(User).values(
                    full_name="Участник фио тут",
                    login='member',
                    password=hashed_password,
                    role='MEMBER'
                )
            )
            conn.commit()  # Commit the transacti
            
            