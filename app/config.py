# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Lista de Tareas API"
    APP_VERSION: str = "1.0.0"
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./tareas.db"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-here"  # Cambiar en producción
    REFRESH_SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configuración de contraseñas
    MIN_PASSWORD_LENGTH: int = 8
    PASSWORD_REGEX: str = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 200  # Límite general de solicitudes por minuto
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 20  # Límite de intentos de login por minuto
    TASK_RATE_LIMIT_PER_MINUTE: int = 100  # Límite de operaciones de tareas por minuto
    
    # Configuración de CORS
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 