from typing import Annotated
from fastapi import Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import database
from app.models.user import User
import jwt
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Bearer")
SessionDep = Annotated[AsyncSession, Depends(database.get_session)]

async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    """Получение юзера по jwt токену который находится в cookie"""

    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Token not found in cookies"})    
    
        decoded_token = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        if not decoded_token.get('sub'):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Token is missing 'sub' claim"})
        
        user = await User.get_by_id(session=session, user_id=decoded_token['sub'])

        if decoded_token['pwd_changed_at'] == user.password_changed_at.timestamp():
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Token has expired"})    
    
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Token has expired"})    
    
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid token"})    
    

UserTokenDep = Annotated[User, Depends(get_current_user)]



