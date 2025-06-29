# app/schemas.py
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re
from app.config import settings

# Esquemas de autenticación
class UsuarioBase(BaseModel):
    """Base común para todas las operaciones de usuario"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v

class UsuarioCrear(UsuarioBase):
    """Esquema para creación de usuarios"""
    password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH)

    @field_validator('password')
    @classmethod
    def password_validation(cls, v: str) -> str:
        if not re.match(settings.PASSWORD_REGEX, v):
            raise ValueError(
                'La contraseña debe tener al menos 8 caracteres, '
                'una letra y un número'
            )
        return v

class UsuarioLogin(BaseModel):
    """Esquema para login de usuarios"""
    email: EmailStr
    password: str
    device_info: Optional[str] = None

class Usuario(UsuarioBase):
    """Esquema para respuesta de usuario (sin password)"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

class TokenData(BaseModel):
    """Esquema para datos del token"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    token_type: Optional[str] = None

class RefreshTokenCreate(BaseModel):
    """Esquema para creación de refresh token"""
    token: str
    device_info: Optional[str] = None

class RefreshTokenResponse(BaseModel):
    """Esquema para respuesta de refresh token"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

# Esquemas de tareas
class TareaBase(BaseModel):
    """Esquema base para tareas"""
    titulo: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    completado: bool = False
    prioridad: int = Field(1, ge=1, le=3)

class TareaCreate(TareaBase):
    """Esquema para crear tareas"""
    pass

class TareaUpdate(TareaBase):
    """Esquema para actualizar tareas"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=100)
    completado: Optional[bool] = None
    prioridad: Optional[int] = Field(None, ge=1, le=3)

class Tarea(TareaBase):
    """Esquema para respuestas de tareas"""
    id: int
    usuario_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TareaListResponse(BaseModel):
    """Esquema para respuesta de lista de tareas con paginación"""
    items: List[Tarea]
    total: int
    page: int
    size: int
    pages: int