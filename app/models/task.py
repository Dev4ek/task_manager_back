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
from app.schemas import task as task_schemas

class Task(Base):
    __tablename__ = 'task'

    uuid: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[task_schemas.TaskStatus] = mapped_column(Enum(task_schemas.TaskStatus), default=task_schemas.TaskStatus.todo)  # Используем перечисление
    comment: Mapped[str] = mapped_column(String(150), nullable=True)
    project_uuid: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey('project.uuid'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")

    @staticmethod
    async def create_task(session: AsyncSession, payload: task_schemas.TaskCreate) -> 'Task':
        """
        Создание новой задачи в базе данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            payload (user_schemas.TaskCreate): Данные новой задачи.
            
        Returns:
            Task: Новая созданная задача.
        """
        
        new_task = Task(
            title=payload.title,
            description=payload.description,
            user_id=payload.user_id,
            project_uuid=payload.project_uuid,
        )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task
    
    @staticmethod
    async def get_all(session: AsyncSession, start_date: datetime = None, end_date: datetime = None, user_id: int = None) -> List['Task']:
        """
        Получение всех задач из базы данных с фильтрацией.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            start_date (datetime): Начальная дата для фильтрации.
            end_date (datetime): Конечная дата для фильтрации.
            responsible_user_id (int): ID ответственного лица.

        Returns:
            List[Task]: Список всех задач.
        """

        stmt = select(Task).options(selectinload(Task.user))

        # Добавление фильтров
        filters = []
        if start_date:
            filters.append(Task.created_at >= start_date)
        if end_date:
            filters.append(Task.created_at <= end_date)
        if user_id:
            filters.append(Task.user_id == user_id)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_uuid(session: AsyncSession, task_uuid: UUID) -> Optional['Task']:
        """
        Получение задачи по его идентификатору.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            task_id (int): Идентификатор задачи.
            
        Returns:
            Optional[Task]: Объект задачи, если найдена, иначе None.
        """
        
        stmt = (
            select(Task)
            .options(selectinload(Task.user))
            .filter(Task.uuid == task_uuid)
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        return task
    
    @staticmethod
    async def delete_task(session: AsyncSession, task_uuid: UUID) -> bool:
        """
        Удаление задачи из базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            task_id (int): Идентификатор задачи.
        """
        
        stmt = delete(Task).filter(Task.uuid == task_uuid)
        await session.execute(stmt)
        await session.commit()
        
        return True