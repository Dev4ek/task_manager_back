from pydantic import BaseModel
from typing import Optional, List
import enum
from app.schemas import user as user_schemas
from datetime import datetime
from uuid import UUID

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int
    project_uuid: UUID
        
class TaskStatus(enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'
    
class TaskInfo(BaseModel):
    uuid: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    comment: Optional[str] = None
    project_uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    user: user_schemas.InfoUser
    
class ProjectInfo(BaseModel):
    uuid: UUID
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskInfo]
        