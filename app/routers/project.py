from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status, Path
from fastapi.responses import JSONResponse, FileResponse
from app.core.dependencies import SessionDep
from app.models.task import Task
from app.schemas import task as task_schemas
from app.models.user import User
from app.utils import user as user_utils
from app.schemas import user as user_schemas
from app.core.dependencies import UserTokenDep
from app.models.project import Project
from app.schemas import project as project_schemas
import pandas as pd



router_project = APIRouter(prefix="/project", tags=["Проект"])

@router_project.post(
    path="",
    summary="Создать проект"
)
async def create_project(
    session: SessionDep,
    payload: project_schemas.ProjectCreate,
    current_user: UserTokenDep,
):
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Доступ запрещен"})
    
    new_project = await Project.create_project(session, payload)
    return new_project


@router_project.get(
    path="",
    summary="Получить все проекты",
    response_model=List[task_schemas.ProjectInfo]
)
async def get_projects(
    session: SessionDep,
    current_user: UserTokenDep,
):
    projects = await Project.get_all(session)
    return projects    
    
    
@router_project.delete(
    path="/{project_uuid}",
    summary="Удалить проект",
    # response_model=List[task_schemas.ProjectInfo]
)
async def delete_project(
    session: SessionDep,
    current_user: UserTokenDep,
    project_uuid = Path(..., title="UUID проекта")
):
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Доступ запрещен"})
    
    project = await Project.get_by_uuid(session, project_uuid)
    
    if project is None:
        raise HTTPException(status_code=404, detail={"message": "Проект не найден"})
    
    await Project.delete_project(session, project_uuid)
    return {"message": "Проект удален"}

@router_project.get(
    path="/{project_uuid}",
    summary="Получить проект по UUID",
    response_model=task_schemas.ProjectInfo
)
async def get_project_by_id(
    session: SessionDep,
    project_uuid: UUID,
    current_user: UserTokenDep,
):
    project = await Project.get_by_uuid(session, project_uuid)
    if project is None:
        raise HTTPException(status_code=404, detail={"message": "Проект не найден"})
    return project


    
@router_project.put("/{project_uuid}")
async def update_project(
    project_uuid: UUID,
    session: SessionDep,
    title: Optional[str] = None,
    description: Optional[str] = None,
):
    project = await Project.get_by_uuid(session, project_uuid)
    if not project:
        raise HTTPException(status_code=404, detail={"message":"Project not found"})

    if title is not None:
        project.title = title
    if description is not None:
        project.description = description
    
    await session.commit()
    await session.refresh(project)

    return project


@router_project.get(
    path="/{project_uuid}/tasks.xlsx",
    summary="Экспортировать задачи в Excel",
)
async def export_tasks(
    project_uuid: UUID,
    session: SessionDep,
):
    project = await Project.get_by_uuid(session, project_uuid)
    if not project:
        raise HTTPException(status_code=404, detail={"message":"Project not found"})

    tasks_data = []
    
    for task in project.tasks:
        print("Вошли в цикл")

        tasks_data.append({
            "Заголовок": task.title,
            "Описание": task.description,
            "Ответственный": task.user.full_name,
            "Комментарии": task.comment
        })

    df = pd.DataFrame(tasks_data)
    df.to_excel("tasks_export.xlsx", index=False)

    return FileResponse("tasks_export.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="tasks.xlsx")