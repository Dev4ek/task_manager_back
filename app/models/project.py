from sqlalchemy import String, BigInteger, Sequence, DateTime, UUID as PostgresUUID, delete, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from app.core.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from app.models.task import Task
from app.models import project as project_schemas

class Project(Base):
    __tablename__ = 'project'

    uuid: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    tasks = relationship("Task", back_populates="project")

    @staticmethod
    async def create_project(session: AsyncSession, payload: project_schemas) -> 'Project':
        new_project = Project(title=payload.title, description=payload.description)
        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)
        return new_project
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List['Project']:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.tasks).selectinload(Task.user)
            )
        )
        
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_uuid(session: AsyncSession, project_uuid: UUID) -> Optional['Project']:
        stmt = (
            select(Project)
            .filter(Project.uuid == project_uuid)
            .options(
                selectinload(Project.tasks).selectinload(Task.user)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_project(session: AsyncSession, project_uuid: UUID) -> bool:
        stmt = delete(Project).filter(Project.uuid == project_uuid)
        await session.execute(stmt)
        await session.commit()
        return True
    