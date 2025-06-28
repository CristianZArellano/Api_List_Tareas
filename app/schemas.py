# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class TareaBase(BaseModel):
    """Base común para todas las operaciones de tarea"""
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    completado: Optional[bool] = Field(default=None)

class TareaCrear(BaseModel):
    """Esquema para creación de tareas (campos requeridos)"""
    titulo: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    completado: bool = Field(default=False)

class TareaActualizar(TareaBase):
    """Esquema para actualización de tareas (todos los campos opcionales)"""
    pass
class Tarea(TareaBase):
    """Esquema para respuesta de tarea (incluye ID)"""
    id: int = Field(...)

    class Config:
        orm_mode = True