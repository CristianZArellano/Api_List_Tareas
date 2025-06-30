# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, IntegrityError
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from app import models, schemas
from app.security import get_password_hash
from app.config import settings
from typing import List, Optional, Tuple

# Operaciones CRUD para usuarios
def get_usuario(db: Session, usuario_id: int) -> Optional[models.Usuario]:
    """Obtiene un usuario por su ID"""
    try:
        result = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al obtener usuario: {str(e)}"
        )

def get_usuario_by_email(db: Session, email: str) -> Optional[models.Usuario]:
    """Obtiene un usuario por su email"""
    try:
        result = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al obtener usuario: {str(e)}"
        )

def create_usuario(db: Session, usuario: schemas.UsuarioCrear) -> models.Usuario:
    """Crea un nuevo usuario"""
    try:
        # Verificar si el email ya existe
        if get_usuario_by_email(db, usuario.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar si el username ya existe
        existing_user = db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        hashed_password = get_password_hash(usuario.password)
        db_usuario = models.Usuario(
            email=usuario.email,
            username=usuario.username,
            hashed_password=hashed_password
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

def update_last_login(db: Session, usuario: models.Usuario) -> models.Usuario:
    """Actualiza la fecha del último login de un usuario"""
    try:
        setattr(usuario, "last_login", datetime.now(timezone.utc))
        db.commit()
        db.refresh(usuario)
        return usuario
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar último login: {str(e)}"
        )

# Operaciones CRUD para refresh tokens
def create_refresh_token(
    db: Session,
    usuario_id: int,
    token: str
) -> models.RefreshToken:
    """Crea un nuevo refresh token"""
    try:
        db_token = models.RefreshToken(
            token=token,
            usuario_id=usuario_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear refresh token: {str(e)}"
        )

def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    """Obtiene un refresh token por su valor"""
    try:
        return db.query(models.RefreshToken).filter(
            and_(
                models.RefreshToken.token == token,
                models.RefreshToken.is_revoked == False,
                models.RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        ).first()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener refresh token: {str(e)}"
        )

def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoca un refresh token"""
    try:
        db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
        if db_token:
            setattr(db_token, "is_revoked", True)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al revocar refresh token: {str(e)}"
        )

def revoke_all_user_tokens(db: Session, usuario_id: int) -> None:
    """Revoca todos los refresh tokens de un usuario"""
    try:
        db.query(models.RefreshToken).filter(
            and_(
                models.RefreshToken.usuario_id == usuario_id,
                models.RefreshToken.is_revoked == False
            )
        ).update({"is_revoked": True})
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al revocar tokens de usuario: {str(e)}"
        )

# Operaciones CRUD para tareas
def get_tarea(db: Session, tarea_id: int, usuario_id: int) -> Optional[models.Tarea]:
    """Obtiene una tarea por su ID y usuario"""
    return db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.usuario_id == usuario_id
    ).first()

def get_tareas(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 10,
    completado: Optional[bool] = None,
    prioridad: Optional[int] = None,
    buscar: Optional[str] = None,
    ordenar_por: str = "created_at",
    orden: str = "desc"
) -> Tuple[List[models.Tarea], int]:
    """
    Obtiene una lista de tareas con filtros y ordenamiento.
    Retorna una tupla con la lista de tareas y el total de tareas.
    """
    try:
        query = db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id)
        
        # Aplicar filtros
        if completado is not None:
            query = query.filter(models.Tarea.completado == completado)
        if prioridad is not None:
            query = query.filter(models.Tarea.prioridad == prioridad)
        if buscar:
            query = query.filter(
                or_(
                    models.Tarea.titulo.ilike(f"%{buscar}%"),
                    models.Tarea.descripcion.ilike(f"%{buscar}%")
                )
            )
        
        # Obtener total antes de aplicar paginación
        total = query.count()
        
        # Aplicar ordenamiento
        order_column = getattr(models.Tarea, ordenar_por, None)
        if not order_column:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Campo de ordenamiento '{ordenar_por}' no válido"
            )
            
        if orden.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
            
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        return query.all(), total
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas: {str(e)}"
        )

def get_tareas_count(
    db: Session,
    usuario_id: int,
    completado: Optional[bool] = None,
    prioridad: Optional[int] = None,
    buscar: Optional[str] = None
) -> int:
    """
    Obtiene el total de tareas que coinciden con los filtros.
    """
    try:
        query = db.query(func.count(models.Tarea.id)).filter(models.Tarea.usuario_id == usuario_id)
        
        # Aplicar filtros
        if completado is not None:
            query = query.filter(models.Tarea.completado == completado)
        if prioridad is not None:
            query = query.filter(models.Tarea.prioridad == prioridad)
        if buscar:
            query = query.filter(
                or_(
                    models.Tarea.titulo.ilike(f"%{buscar}%"),
                    models.Tarea.descripcion.ilike(f"%{buscar}%")
                )
            )
            
        return query.scalar()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener total de tareas: {str(e)}"
        )

def create_tarea(db: Session, tarea: schemas.TareaCreate, usuario_id: int) -> models.Tarea:
    """Crea una nueva tarea"""
    db_tarea = models.Tarea(
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        completado=tarea.completado,
        prioridad=tarea.prioridad,
        usuario_id=usuario_id
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

def update_tarea(db: Session, tarea: models.Tarea, tarea_update: schemas.TareaUpdate) -> models.Tarea:
    """Actualiza una tarea existente"""
    # Actualizar solo los campos proporcionados
    update_data = tarea_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tarea, key, value)
    
    # SQLAlchemy actualizará automáticamente updated_at con onupdate=func.now()
    
    db.commit()
    db.refresh(tarea)
    return tarea

def delete_tarea(db: Session, tarea: models.Tarea) -> None:
    """Elimina una tarea"""
    db.delete(tarea)
    db.commit()