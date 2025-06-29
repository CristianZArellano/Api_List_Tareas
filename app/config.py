# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional, ClassVar, Dict, Set
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
    
    # Configuración de contraseñas - Requisitos de seguridad mejorados
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    # Permitir letras Unicode, números y caracteres especiales estándar
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ ])[\w\d!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ áéíóúüñÑÁÉÍÓÚÜ]{8,128}$"
    
    # Mensajes de error para validación de contraseñas
    PASSWORD_ERROR_MESSAGES: ClassVar[Dict[str, str]] = {
        "too_short": "La contraseña debe tener al menos 8 caracteres.",
        "too_long": "La contraseña no puede tener más de 128 caracteres.",
        "no_lowercase": "La contraseña debe contener al menos una letra minúscula (de cualquier idioma).",
        "no_uppercase": "La contraseña debe contener al menos una letra mayúscula (de cualquier idioma).",
        "no_digit": "La contraseña debe contener al menos un número (0-9).",
        "no_special": "La contraseña debe contener al menos un carácter especial (por ejemplo: !@#$%&*? y similares).",
        "invalid_chars": "La contraseña solo puede contener letras de cualquier idioma, números y caracteres especiales estándar: !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ y espacio.",
        "common_password": "La contraseña es demasiado común, elige una más segura.",
        "sequential_chars": "La contraseña no puede contener secuencias de caracteres (ej: 123, abc).",
        "repeated_chars": "La contraseña no puede contener caracteres repetidos más de 3 veces consecutivas."
    }
    
    # Contraseñas comunes que no se permiten
    COMMON_PASSWORDS: ClassVar[Set[str]] = {
        "password", "123456", "123456789", "qwerty", "abc123", "password123",
        "admin", "letmein", "welcome", "monkey", "dragon", "master", "hello",
        "freedom", "whatever", "qazwsx", "trustno1", "jordan", "harley",
        "ranger", "iwantu", "jennifer", "hunter", "buster", "soccer",
        "baseball", "tiger", "charlie", "andrew", "michelle", "love",
        "sunshine", "jessica", "asshole", "696969", "amanda", "access",
        "yankees", "987654321", "dallas", "austin", "thunder", "taylor",
        "matrix", "mobilemail", "mom", "monitor", "monitoring", "montana",
        "moon", "moscow", "mother", "movie", "mozilla", "music", "mustang",
        "password", "pa$$w0rd", "p@ssw0rd", "pass123", "pass1234", "pass12345"
    }
    
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