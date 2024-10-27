from pydantic import AnyHttpUrl, ConfigDict, BaseModel
from pydantic_settings import BaseSettings
import os
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    # Основные настройки приложения
    PROJECT_NAME: str = "Task management"
    PROJECT_VERSION: str = "1.0.0"
    PRODUCTION_URL: str = "http://localhost:8082"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 #TODO: change time to 10 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60 * 24 * 30  # 30 days
    
    CRYPTOGRAPHY_KEY: str
    
    BROKER_URL: str
    ELASTICSEARCH_URL: str 

    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    
    SQLALCHEMY_DATABASE_URL: str
    SQLALCHEMY_DATABASE_SYNC_URL: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")   

# Инициализируем объект настроек
settings = Settings()
cipher_suite = Fernet(settings.CRYPTOGRAPHY_KEY)