# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from fastapi import HTTPException, status
from app import models, schemas


def get_tarea(db: Session, tarea_id: int):
    """Obtiene una tarea por su ID con manejo de errores."""
    try:
        result = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).one()
        return result
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al obtener tarea: {str(e)}"
        )


def get_tareas(db: Session, skip: int = 0, limit: int = 100, completado: bool | None = None):
    """Obtiene tareas paginadas con filtro opcional por estado de completado."""
    try:
        query = db.query(models.Tarea)
        
        # Aplicar filtro si se especifica
        if completado is not None:
            query = query.filter(models.Tarea.completado == completado)
            
        # Asegurar parámetros de paginación válidos
        safe_skip = max(0, skip)
        safe_limit = min(500, max(1, limit))  # Límite entre 1 y 500
        
        return (
            query.order_by(models.Tarea.id)
                .offset(safe_skip)
                .limit(safe_limit)
                .all()
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas: {str(e)}"
        )


def create_tarea(db: Session, tarea: schemas.TareaCrear):
    """Crea una nueva tarea con manejo de errores transaccionales."""
    try:
        db_tarea = models.Tarea(**tarea.model_dump())
        db.add(db_tarea)
        db.commit()
        db.refresh(db_tarea)
        return db_tarea
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tarea: {str(e)}"
        )


def update_tarea(db: Session, tarea_id: int, datos: schemas.TareaActualizar):
    """Actualiza una tarea existente con validación completa."""
    try:
        db_tarea = get_tarea(db, tarea_id)
        if not db_tarea:
            return None
            
        # Actualizar solo los campos proporcionados
        update_data = datos.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tarea, key, value)
            
        db.commit()
        db.refresh(db_tarea)
        return db_tarea
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar tarea: {str(e)}"
        )


def delete_tarea(db: Session, tarea_id: int):
    """Elimina una tarea con manejo transaccional seguro."""
    try:
        db_tarea = get_tarea(db, tarea_id)
        if not db_tarea:
            return None
            
        db.delete(db_tarea)
        db.commit()
        return db_tarea
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tarea: {str(e)}"
        )