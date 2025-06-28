# app/models.py
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    completado = Column(Boolean, default=False)
