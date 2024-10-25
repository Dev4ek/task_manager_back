import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, insert, create_engine
from api.utils import search as search_utils
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
    Base.metadata.drop_all(engine_sync)
    # search_utils.delete_index("products")
    # search_utils.create_index("products")
    Base.metadata.create_all(engine_sync, checkfirst=True)
    

def create_test_user():
    with engine_sync.connect() as conn:
        
        result = conn.execute(
            select(User)
            .filter(User.nickname == 'admin')
        ).first()
        
        if result is None:  # user not exist
            conn.execute(
                insert(User)
                .values(
                    nickname='admin',
                    password=hash_password('admin'),
                    email='admin@mail.ru'
                )
            )
            conn.commit()  # Commit the transaction
            
            