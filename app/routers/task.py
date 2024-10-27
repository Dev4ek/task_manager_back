from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status, Path
from fastapi.responses import JSONResponse
from app.core.dependencies import SessionDep
from app.models.task import Task
from app.schemas import task as task_schemas
from app.models.user import User
from app.utils import user as user_utils
from app.schemas import user as user_schemas
from app.core.dependencies import UserTokenDep


router_task = APIRouter(prefix="/task", tags=["Задачи"])

@router_task.post(
    path="",
    summary="Создать задачу"
)
async def create_task(
    session: SessionDep,
    payload: task_schemas.TaskCreate,
    current_user: UserTokenDep,
):
    user = await User.get_by_id(session, payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Пользователь не найден"})
    
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Access denied"})
    
    new_task = await Task.create_task(session, payload)
    return new_task

@router_task.get(
    path="",
    response_model=List[task_schemas.TaskInfo],
    summary="Получить все задачи"
)
async def get_tasks(
    session: SessionDep,
    current_user: UserTokenDep,
    start_date: datetime = Query(None, description="Начальная дата фильтрации"),
    end_date: datetime = Query(None, description="Конечная дата фильтрации"),
    user_id: int = Query(None, description="ID пользователя"),
):
    tasks = await Task.get_all(session, start_date=start_date, end_date=end_date, user_id=user_id)
    return tasks

@router_task.get(
    path="/{task_uuid}",
    response_model=task_schemas.TaskInfo,
    summary="Получить информацию о задаче"
)
async def get_task_by_id(
    task_uuid: UUID,
    session: SessionDep
):
    task = await Task.get_by_uuid(session, task_uuid)
    if task is None:
        raise HTTPException(status_code=404, detail={"message": "Task not found"})
    return task

@router_task.put(
    path="/{task_uuid}",
    summary="Изменить данные о задаче"
)
async def update_task(
    task_uuid: UUID,
    session: SessionDep,
    current_user: UserTokenDep,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    status_task: Optional[task_schemas.TaskStatus] = Query(None),
    comment: Optional[str] = Query(None),
):
    task = await Task.get_by_uuid(session, task_uuid)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Task not found"})

    # Проверка прав доступа
    if current_user.role == user_schemas.Roles.ADMIN:
        # Админ может изменять все поля задачи
        pass
    elif current_user.role == user_schemas.Roles.MEMBER:
        # Обычный пользователь может изменять только статус и комментарий задачи, если она своя
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "Member can only modify their own tasks"}
            )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Access denied"})

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status_task is not None:
        task.status = status_task
    if comment is not None:
        task.comment = comment

    await session.commit()
    session.refresh(task)
    return task

@router_task.delete(
    path="/{task_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить задачу"
)
async def delete_task(
    task_uuid: UUID,
    session: SessionDep,
    current_user: UserTokenDep
):
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Access denied"})
    
    task = await Task.get_by_uuid(session, task_uuid)
    if task is None:
        raise HTTPException(status_code=404, detail={"message": "Task not found"})

    await Task.delete_task(session, task_uuid)  # Implement this method in your Task model
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Успешно удалено"})