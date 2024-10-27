from pydantic import BaseModel, EmailStr, Field, validator, field_validator
import enum
import re
from fastapi import HTTPException, status
from datetime import datetime

class Roles(enum.Enum):
    """Схема ролей для пользователей"""
    
    GUEST = "guest"
    MEMBER = "member"
    ADMIN = "admin"
    
class Signin(BaseModel):
    """Схема для логина"""
    
    login: str
    password: str
    
class Signup(BaseModel):
    """Регистрация пользователя"""

    full_name: str = Field(..., description="Полное имя с пробелами и дефисами.")
    login: str = Field(..., description="Имя пользователя максимум 20 символов.")
    password: str = Field(..., description="Пароль длиной не более 20 символов.")
    confirm_password: str = Field(..., description="Подтверждение пароля.")

    @validator('full_name')
    def validate_full_name(cls, value):
        if not re.match(r'^[А-Яа-яЁё\s-]+$', value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'ФИО должно содержать только кириллические буквы, пробелы или дефисы.'})
        if len(value) > 50:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'ФИО не должно превышать 50 символов.'})
        
        words = value.split()
        if len(words) != 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'ФИО должно содержать три слова.'})

        return value
    
    @validator('login')
    def validate_login(cls, value):
        if len(value) > 20:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'Логин должен быть длиной не более 20 символов.'})
        if ' ' in value or not re.match(r'^[\w-]+$', value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'Логин не должен содержать пробелов и специальных символов, кроме дефиса.'})
        
        return value

    @validator('password')
    def validate_password(cls, value):
        if len(value) > 20:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'Пароль должен быть длиной не более 20 символов.'})
        if ' ' in value or not re.match(r'^[\w-]+$', value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'Пароль не должен содержать пробелов и специальных символов, кроме дефиса.'})
        
        return value

    @validator('confirm_password')
    def passwords_match(cls, value, values):
        if 'password' in values and value != values['password']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": 'Пароли не совпадают.'})
        return value
    
    
    
class User(BaseModel):
    """Схема для пользователей"""
    id: int
    full_name: str
    role: Roles
    avatar_image: str

    
class LoginSuccessful(BaseModel):
    """Схема для ответа 200 OK"""
    message: str
    token: str
    
class WrongLoginOrPaswd(BaseModel):
    """Схема для ответа 401 Unauthorized"""
    message: str = "Неправильный логин или пароль"

class LoginConflict(BaseModel):
    """Схема для ответа 409 Conflict"""
    message: str = "Логин уже занят"
    
class WrongValidationFullNameRussia(BaseModel):
    """Схема для ответа 400 Bad Request"""
    message: str = "ФИО должно содержать только кириллические буквы, пробелы или дефисы."
    
class WrongValidationFullNameLen(BaseModel):
    """Схема для ответа 400 Bad Request"""
    message: str = "ФИО не должно превышать 50 символов."
    
class WrongValidationPasswordLen(BaseModel):
    """Схема для ответа 400 Bad Request"""
    message: str = "Пароль длиной не более 20 символов."
    
class WrongValidationPasswordRepeat(BaseModel):
    """Схема для ответа 400 Bad Request"""
    message: str = "Пароли не совпадают"


class InfoUser(BaseModel):
    """Схема для ответа информации о пользователе"""
    id: int
    full_name: str
    role: Roles
    avatar_image: str
    created_at: datetime

class UserNotFound(BaseModel):
    """Схема для ответа 404 Not Found"""
    message: str = "Пользователь не найден"
    