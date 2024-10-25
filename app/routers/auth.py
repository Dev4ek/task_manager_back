from typing import Any, Dict, List
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status, Path
from fastapi.responses import JSONResponse
from app.schemas import 

router_auth = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router_auth.post(
    path="/signin",
    summary="Авторизация пользователя",
    description="Авторизация пользователя по логину и паролю",
    status_code=status.HTTP_200_OK,
)
async def signin(
    payload: 
    session: SessionDep,
    response: Response
):
    current_user = await User.authenticate(session, payload.nickname_or_email, payload.password)
    if not current_user:
        content = main_schemas.Error(
            type_error="incorrect data",
            message="Неправильный логин или пароль"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=content)

    try:
        access_token = await auth_utils.create_access_token(current_user)
        session_token = await auth_utils.create_session(current_user, session)
            
        return schemas_auth.Login.LoginOUT(
            token=access_token, 
            session=session_token, 
            already=True
        )
        
    except Exception:  # Конкретизируем ошибки
        content = main_schemas.Error(
            type_error="SERVER_ERROR",
            message="При авторизации произошла внутреняя ошибка сервера"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=content)

    # async with httpx.AsyncClient() as client:
    #     cookies = response.headers.getlist("set-cookie")
    #     cookies_dict = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookies}

    #     user_info_response = await client.get("http://localhost:8082/user/info", cookies=cookies_dict)
    #     user_info = user_info_response.json()
    
    # return JSONResponse(status_code=status.HTTP_200_OK, content=user_info, headers=response.headers)

@router_auth.post(
    path="/refresh",
    summary="Обновление access токена",
    status_code=status.HTTP_200_OK,
    response_model=schemas_auth.Login.LoginOUT,
    responses=schemas_auth.RefreshToken.responses,
)
async def refresh_token(
    request: Request,
    session: SessionDep,
    response: Response
):
    session_token = request.cookies.get("session")
    
    content_error = main_schemas.Error(
            type_error="FORBIDDEN",
            message="Session token not found"
    ).model_dump()
    
    if not session_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=content_error)

    user_id = await Session.get_user_id_by_token(session, session_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=content_error)
    
    try:
        current_user = await User.get_by_id(session, user_id)
        await Session.remove_session(session, session_token)
        
        new_access_token = await auth_utils.create_access_token(current_user)
        new_session_token = await auth_utils.create_session(current_user, session)
    
        return schemas_auth.Login.LoginOUT(
            token=new_access_token, 
            session=new_session_token, 
            already=True
        )
    
    except Exception as e:
        content = main_schemas.Error(
            type_error="SERVER_ERROR",
            message="При авторизации произошла внутреняя ошибка сервера"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=content)
    



@router_auth.post(
    path="/logout",
    summary="Выйти с аккаунта",
    description="Удаляет куки и сессию",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=schemas_auth.logout.responses,
)
async def logout(
    session: SessionDep,
    response: Response,
    request: Request,
):
    user_token = request.cookies.get('token') 
    user_session = request.cookies.get('session') 
    
    await Session.remove_session(session, user_session)
  
    response.delete_cookie("token")
    response.delete_cookie("session")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=response.headers)
        
    
@router_auth.put(
    path="/signup",
    summary="Регистрация пользователя",
    description="После регистрации уникальная ссылка с токеном генерируется и отправляется пользователю",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_auth.Login.LoginOUT,
    responses=schemas_auth.Signup.responses
)
async def signup(
    session: SessionDep,
    payload: schemas_auth.Signup.signIN,
    response: Response,
    request: Request,
):
    user_nickname = await User.check_nickname(session, payload.nickname)
    if user_nickname:
        content = main_schemas.Error(type_error="nickname", message="Это имя пользователя уже занято").model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=content)
    
    user_email = await User.check_email(session, payload.email)
    if user_email:
        content = main_schemas.Error(type_error="email", message="Такая почта уже зарегистрирована").model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=content)
    
    try:
        new_user = await User.signup(session, payload.nickname, payload.password, payload.email)
        email_verify = await EmailVerify.create_verify(session, new_user.id)
        # email_task.send_verify_url.delay(email_verify.user.email, email_verify.token)
        
        access_token = await auth_utils.create_access_token(new_user)
        session_token = await auth_utils.create_session(new_user, session)
        
        encrypted_user_ref = request.cookies.get('ref')
        
        if encrypted_user_ref:
            try:
                decrypted_user_ref = cipher_suite.decrypt(encrypted_user_ref)
                user_ref = int(decrypted_user_ref.decode())

                await Referall.add_referall(session, user_ref, new_user.id)
                await User.update_is_ref(session, new_user.id)
                
            except Exception as e:
                ic(f"Ошибка дешифрования реферала: {encrypted_user_ref}")
                encrypted_user_ref = None
                
        return schemas_auth.Login.LoginOUT(
            token=access_token, 
            session=session_token, 
            already=True
        )
        
        async with httpx.AsyncClient() as client:
            cookies = response.headers.getlist("set-cookie")
            cookies_dict = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookies}

            user_info_response = await client.get("http://localhost:8082/user/info", cookies=cookies_dict)
            user_info = user_info_response.json()
        
            return JSONResponse(status_code=status.HTTP_200_OK, content=user_info, headers=response.headers)
    
    except Exception as e:
        print(e)
        content = main_schemas.Error(type_error="SERVER_ERROR", message="При регистрации произошла внутреняя ошибка сервера, попробуйте еще раз").model_dump()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=content)


@router_auth.get(
    path="/email-verify/{token}",
    summary="Подтверждение почты",
    description="При переходе по этой ссылке у пользователя подтверждается почта",
    status_code=status.HTTP_200_OK,
)
async def email_verify(
    session: SessionDep,
    token: str = Path(..., description="Уникальный токен для подтверждения почты человека"),
):
    email_verify = await EmailVerify.verify_token(session, token)
    
    if email_verify:
        await User.verify_email(session, email_verify.user_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content="Почта подтверждена")
    
    content = main_schemas.Error(type_error="token", message="Токен для подтверждения почты недействителен или устарел").model_dump()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=content)

@router_auth.post(
    '/set-cookie'
)
async def set_cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    payload: Dict = Body(...),
):
    for key, value in payload.items():
        if key and value:
            response.set_cookie(
                key=key,
                value=value,
                httponly=False,
                secure=True,
                max_age=60 * 60 * 24 * 7,
                samesite="None"
            )
    
    return Response(status_code=status.HTTP_200_OK, headers=response.headers)
    
   