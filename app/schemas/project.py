from pydantic import BaseModel
from typing import Optional, List
import enum
from app.schemas import user as user_schemas
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
