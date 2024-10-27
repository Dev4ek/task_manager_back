from app.models.user import User
import bcrypt
import pytz
from datetime import datetime, timedelta
from app.core.config import settings
import jwt
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
from io import BytesIO
from uuid import UUID, uuid4
import os

async def hash_password(plain_password: str) -> str:
    """
    Хеширует предоставленный пароль с использованием bcrypt.

    Args:
        plain_password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

async def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли предоставленный пароль с хешированным паролем.

    Args:
        plain_password (str): Пароль для проверки.
        hashed_password (str): Хешированный пароль, с которым производится сравнение.

    Returns:
        bool: True, если пароли совпадают, False - в противном случае.
    """
    
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def get_moscow_time():
    """Возвращает текущее московское время."""
    
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    
    return moscow_time


async def create_access_token(user: User):
    """Создать авторизационный токен"""
    
    moscow_time = await get_moscow_time()
    expire = (moscow_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    
    jwt_data = {
        "sub": user.id,
        "exp": expire,
        "pwd_changed_at": user.password_changed_at.timestamp()
    }
    
    encoded_token = jwt.encode(jwt_data, settings.SECRET_KEY, "HS256")
    return encoded_token


async def create_refresh_token(user: User):
    """Создать refresh-токен"""

    moscow_time = await get_moscow_time()
    expire = (moscow_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()

    jwt_data = {
        "sub": user.id,
        "exp": expire,
    }

    encoded_refresh_token = jwt.encode(jwt_data, settings.SECRET_KEY, "HS256")
    return encoded_refresh_token

async def get_user_by_refresh_token(session: AsyncSession, refresh_token: str):
    """Получить пользователя по refresh-токену"""

    try:
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Refresh token не указан"})

        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        token_pwd_changed_at = payload.get("pwd_changed_at")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Invalid refresh token"})

        user = await User.get_by_id(session, user_id=user_id)

        if user is None or user.password_changed_at.timestamp() != token_pwd_changed_at:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Refresh token has expired or user password has changed"})

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Refresh token has expired"})

    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Invalid refresh token"})
    
    
    
def _save_image(image: UploadFile, IMAGE_UPLOAD_DIR, quality=75):
    allowed_extensions = (".png", ".jpg", ".jpeg", ".gif")
    
    if not image.filename.endswith(allowed_extensions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Invalid image format. Only PNG, JPG, JPEG, GIF are allowed."})

    file_extension = image.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_extension}"

    filepath = os.path.join(IMAGE_UPLOAD_DIR, filename)

    try:
        # Открываем изображение через Pillow
        img = Image.open(BytesIO(image.file.read()))

        # Если изображение PNG с прозрачностью (RGBA), сохраняем как PNG с оптимизацией
        if img.mode in ("RGBA", "LA"):
            img.save(filepath, format="PNG", optimize=True)

        # Если изображение не прозрачное или в формате JPEG, уменьшаем его вес с параметром качества
        else:
            if img.format in ("JPEG", "JPG"):
                img.save(filepath, format="JPEG", quality=quality, optimize=True)
            else:
                img.save(filepath, format="PNG", optimize=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the image: {str(e)}")

    return filepath

async def save_avatar_image(image: UploadFile):
    if image is None: return None
    IMAGE_UPLOAD_DIR = "static/avatars/"
    return _save_image(image, IMAGE_UPLOAD_DIR)


