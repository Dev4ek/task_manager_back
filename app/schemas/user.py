from pydantic import BaseModel
import enum

class Roles(enum.Enum):
    """Схема ролей для пользователей"""
    
    GUEST = "guest"
    MEMBER = "member"
    ADMIN = "admin"
    
class signin(BaseModel):
    """Схема для логина"""
    
    login: str
    password: str

class signup(BaseModel):
    """Схема для регистрации"""
    
    full_name: str
    login: str
    password: str
    email: str
    role: Roles = Roles.GUEST
    
    