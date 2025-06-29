# app/security.py
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Tuple, Any, cast
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from app.config import settings
import re
from fastapi.security import OAuth2PasswordBearer
import time
from sqlalchemy import Column, Boolean

def get_safe_id(obj: Any) -> int:
    """Extrae el ID de manera segura de un objeto SQLAlchemy"""
    return int(getattr(obj, 'id', 0))

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme para autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Bearer token para autenticación
class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se proporcionó token de autenticación",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise e

security = CustomHTTPBearer()

def get_db():
    """Proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña"""
    return pwd_context.hash(password)

def validate_password(password: str) -> bool:
    """Valida que la contraseña cumpla con los requisitos mínimos"""
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False
    if not re.match(settings.PASSWORD_REGEX, password):
        return False
    return True

def create_token(data: dict, expires_delta: timedelta, secret_key: str) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict) -> str:
    """Crea un token JWT de acceso"""
    return create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.SECRET_KEY
    )

def create_refresh_token(user: models.Usuario) -> str:
    """Crea un token de refresco para el usuario"""
    to_encode = {
        "sub": user.email,
        "type": "refresh",
        "user_id": user.id,
        "timestamp": int(time.time() * 1000)  # Añadir timestamp en milisegundos
    }
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Union[models.Usuario, bool]:
    """Autentica un usuario con email y contraseña"""
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return False
    if not verify_password(password, str(user.hashed_password)):
        return False
    return user

def create_tokens_for_user(user: models.Usuario) -> Dict[str, str]:
    """Crea tokens de acceso y refresco para un usuario"""
    access_token_data = {
        "sub": str(user.email),
        "type": "access",
        "user_id": user.id
    }
    refresh_token_data = {
        "sub": str(user.email),
        "type": "refresh",
        "user_id": user.id
    }
    
    return {
        "access_token": create_access_token(access_token_data),
        "refresh_token": create_refresh_token(user),
        "token_type": "bearer"
    }

def verify_task_ownership(db: Session, tarea_id: int, user_id: int) -> bool:
    """Verifica si una tarea pertenece a un usuario específico"""
    try:
        result = db.query(models.Tarea).filter(
            models.Tarea.id == tarea_id,
            models.Tarea.usuario_id == user_id
        ).first()
        return result is not None
    except Exception:
        return False

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """
    Obtiene el usuario activo actual a partir del token JWT.
    
    - Verifica que el token sea válido
    - Verifica que el usuario exista y esté activo
    - Retorna el usuario si todo es correcto
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_for_tarea(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    tarea_id: Optional[int] = None
) -> models.Usuario:
    """
    Obtiene el usuario actual y verifica la propiedad de la tarea si se proporciona un ID.
    
    Args:
        token: Token de acceso JWT
        db: Sesión de base de datos
        tarea_id: ID opcional de la tarea a verificar
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no tiene acceso a la tarea
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not isinstance(email, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verificar si el usuario está activo usando el atributo directamente
        is_active = getattr(user, 'is_active', False)
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if tarea_id is not None:
            tarea = db.query(models.Tarea).filter(
                models.Tarea.id == tarea_id,
                models.Tarea.usuario_id == get_safe_id(user)
            ).first()
            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarea no encontrada"
                )
                
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def refresh_access_token(refresh_token: str, db: Session) -> Dict[str, str]:
    """Refresca el token de acceso usando un token de refresco"""
    try:
        payload = verify_token(refresh_token, settings.REFRESH_SECRET_KEY)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = db.query(models.Usuario).filter(
            models.Usuario.email == str(payload.get("sub"))
        ).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return create_tokens_for_user(user)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_from_token(token: str) -> Optional[models.Usuario]:
    """Obtiene un usuario a partir de un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
            
        db = SessionLocal()
        try:
            user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
            return user
        finally:
            db.close()
            
    except JWTError:
        return None 