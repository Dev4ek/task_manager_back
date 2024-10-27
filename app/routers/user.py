from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, Response, status, Path, UploadFile
from fastapi.responses import JSONResponse
from app.core.dependencies import SessionDep
from app.schemas import user as user_schemas
from app.models.user import User
from app.utils import user as user_utils
from app.core.dependencies import UserTokenDep

router_user = APIRouter(prefix="/user", tags=["Пользователь"])

@router_user.post(
    path="/signin",
    summary="Авторизация пользователя",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.LoginSuccessful,
    responses={
        401: {"model": user_schemas.WrongLoginOrPaswd}
    }
)
async def signin(
    session: SessionDep,
    payload: user_schemas.Signin
):
    user: Optional[User] = await User.signin(session, payload)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Неправильный логин или пароль"})

    access_token = await user_utils.create_access_token(user)
    refresh_token = await user_utils.create_refresh_token(user)

    return {"message": "Login successful", "token": access_token}



@router_user.post(
    path="/signup",
    summary="Регистрация пользователя",
    response_model=user_schemas.LoginSuccessful,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Ошибка валидации",
            "content": {
                "application/json": {
                    "examples": {
                        "WrongValidationFullName": {
                            "summary": "Ошибка валидации ФИО кириллица",
                            "value": {"detail": "ФИО должно содержать только кириллические буквы, пробелы или дефисы."}
                        },
                        "WrongValidationFullNameLen": {
                            "summary": "Ошибка валидации ФИО длина",
                            "value": {"detail": "ФИО должно быть длиной до 50 символов."}
                        },
                        "WrongValidationPasswordRussia": {
                            "summary": "Ошибка валидации пароля длина",
                            "value": {"detail": "Пароль должен быть длиной не более 20 символов."}
                        },
                        "WrongValidationLoginLen": {
                            "summary": "Ошибка валидации логина длина",
                            "value": {"detail": "Логин должен быть длиной не более 20 символов."}
                        },
                        "WrongValidationPasswordRepeat": {
                            "summary": "Ошибка валидации пароля не совпадают",
                            "value": {"detail": "Пароли не совпадают"}
                        },
                        "WrongValidationPassword": {
                            "summary": "Пароль не должен содержать пробелов и специальных символов, кроме дефиса.",
                            "value": {"detail": "Пароль не должен содержать пробелов и специальных символов, кроме дефиса."}
                        },
                        "WrongValidationLogin": {
                            "summary": "Логин не должен содержать пробелов и специальных символов, кроме дефиса.",
                            "value": {"detail": "Логин не должен содержать пробелов и специальных символов, кроме дефиса."}
                        }
                    }
                }
            }
        },
        409: {
            "model": user_schemas.LoginConflict,
            "description": "Логин уже существует"
        }
    }
)
async def signup(
    session: SessionDep,
    payload: user_schemas.Signup
):
    use_login = await User.check_login(session, payload.login)
    if use_login:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": "Логин уже занят"})
    
    user: Optional['User'] = await User.signup(session, payload)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": "Ошибка при создании пользователя"})
    
    access_token = await user_utils.create_access_token(user)
    refresh_token = await user_utils.create_refresh_token(user)

    return {"message": "Registration successful", "token": access_token}

@router_user.get(
    path="/info",
    summary="Получить информацию об аккаунте",
    response_model=user_schemas.User,
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    session: SessionDep,
    current_user: UserTokenDep,
):
    user = await User.get_by_id(session, current_user.id)
    return user


@router_user.get(
    path="/list",
    summary="Получить список всех пользователей",
    response_model=List[user_schemas.User],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    session: SessionDep,
    current_user: UserTokenDep,
):
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Доступ запрещен"})
    
    users = await User.get_all_users(session)
    return users
    
@router_user.put(
    path="/me",
    response_model=user_schemas.InfoUser
)
async def update_user(
    session: SessionDep,
    current_user: UserTokenDep,
    full_name: Optional[str] = None,
    avatar_image: Optional[UploadFile] = Form(None)
):
    if full_name is not None:
        current_user.full_name = full_name
    
    if avatar_image:
        path_image = await user_utils.save_avatar_image(avatar_image)
        current_user.avatar_image = path_image

    await session.commit()
    await session.refresh(current_user)

    return current_user


@router_user.put(
    path="/id/{user_id}",
    response_model=user_schemas.InfoUser
)
async def update_user(
    session: SessionDep,
    current_user: UserTokenDep,
    full_name: Optional[str] = None,
    description: Optional[str] = None,
    role: Optional[user_schemas.Roles] = None,
    avatar_image: Optional[UploadFile] = Form(None)
):
    if not current_user.role == user_schemas.Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Доступ запрещен"})
        
    if full_name is not None:
        current_user.full_name = full_name
        
    if description is not None:
        current_user.description = full_name
        
    if role is not None:
        current_user.role = role
    
    
    if avatar_image:
        path_image = await user_utils.save_avatar_image(avatar_image)
        current_user.avatar_image = path_image
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user