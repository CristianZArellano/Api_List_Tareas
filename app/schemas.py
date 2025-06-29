# app/schemas.py
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re
from app.config import settings
from app.password_validator import validate_password_strength

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
    password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH, max_length=settings.MAX_PASSWORD_LENGTH)

    @field_validator('password')
    @classmethod
    def password_validation(cls, v: str) -> str:
        is_valid, error_message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

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

class RefreshTokenResponse(BaseModel):
    """Esquema para respuesta de refresh token"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

# Esquemas de tareas
class TareaBase(BaseModel):
    """Esquema base para tareas"""
    titulo: str = Field(..., min_length=1, max_length=100, examples=["Completar proyecto"])
    descripcion: Optional[str] = Field(None, max_length=500, examples=["Finalizar la implementación del módulo de autenticación"])
    completado: bool = Field(default=False, examples=[False])
    prioridad: int = Field(default=1, ge=1, le=3, examples=[1, 2, 3], description="1: Baja, 2: Media, 3: Alta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Completar proyecto",
                "descripcion": "Finalizar la implementación del módulo de autenticación",
                "completado": False,
                "prioridad": 1
            }
        }
    )

class TareaCreate(TareaBase):
    """Esquema para crear tareas"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Completar proyecto",
                "descripcion": "Finalizar la implementación del módulo de autenticación",
                "completado": False,
                "prioridad": 1
            }
        }
    )

class TareaUpdate(BaseModel):
    """Esquema para actualizar tareas"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Completar proyecto actualizado"])
    descripcion: Optional[str] = Field(None, max_length=500, examples=["Finalizar la implementación del módulo de autenticación"])
    completado: Optional[bool] = Field(None, examples=[True, False])
    prioridad: Optional[int] = Field(None, ge=1, le=3, examples=[1, 2, 3], description="1: Baja, 2: Media, 3: Alta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Completar proyecto actualizado",
                "descripcion": "Finalizar la implementación del módulo de autenticación",
                "completado": True,
                "prioridad": 2
            }
        }
    )

class Tarea(TareaBase):
    """Esquema para respuestas de tareas"""
    id: int = Field(examples=[1])
    usuario_id: int = Field(examples=[1])
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "titulo": "Completar proyecto",
                "descripcion": "Finalizar la implementación del módulo de autenticación",
                "completado": False,
                "prioridad": 1,
                "usuario_id": 1,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": None
            }
        }
    )

class TareaListResponse(BaseModel):
    """Esquema para respuesta de lista de tareas con paginación"""
    items: List[Tarea]
    total: int
    page: int
    size: int
    pages: int

class PasswordCheck(BaseModel):
    """Esquema para validación de contraseña"""
    password: str

class PasswordValidationResponse(BaseModel):
    """Respuesta de validación de contraseña"""
    is_valid: bool
    error_message: Optional[str] = None

class PasswordRequirements(BaseModel):
    """Requisitos de contraseña"""
    min_length: int
    max_length: int
    requirements: List[str]

class PasswordStrengthAnalysis(BaseModel):
    """Análisis de fortaleza de contraseña"""
    length: int
    has_uppercase: bool
    has_lowercase: bool
    has_digit: bool
    has_symbol: bool
    has_spaces: bool
    has_repeating_chars: bool
    is_common: bool
    score: int
    strength: str