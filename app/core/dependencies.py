from typing import Annotated, Any, Dict, Optional
from fastapi import Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from api.core import database
from api.models.user import User
import jwt
from api.schemas import main as main_schemas
from api.core.config import settings
from icecream import ic
from api.models import Session

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]

async def get_current_user(request: Request, session: SessionDep):
    """Получение юзера по jwt токену который находится в cookie"""

    try:
        token = request.cookies.get('token')
        session_token = request.cookies.get('session')
        
        if not token:
            content = main_schemas.Error(
                type_error="UNAUTHORIZED",
                message="Token not found in cookies"
            ).model_dump()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=content)    
    
        if not await Session.get_by_session(session, session_token):
            content = main_schemas.Error(
                type_error="FORBIDDEN",
                message="Token has expired"
            ).model_dump()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=content)
    
        decoded_token = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        user = await User.get_by_id(session=session, user_id=decoded_token['sub'])

        if decoded_token['pwd_changed_at'] == user.password_changed_at.timestamp():
            return user
        
        content = main_schemas.Error(
            type_error="FORBIDDEN",
            message="Token has expired"
        ).model_dump()
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=content)    
    

    except jwt.exceptions.ExpiredSignatureError:
        content = main_schemas.Error(
            type_error="FORBIDDEN",
            message="Token has expired"
        ).model_dump()
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=content)    
    
    except jwt.exceptions.DecodeError:
        content = main_schemas.Error(
            type_error="UNAUTHORIZED",
            message="Invalid token"
        ).model_dump()
                
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=content)
    

UserTokenDep = Annotated[User, Depends(get_current_user)]



