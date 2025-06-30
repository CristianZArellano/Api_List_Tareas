from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.security import (
    authenticate_user, create_access_token, get_current_active_user,
    create_refresh_token, create_tokens_for_user, get_user_from_token, get_current_user_for_tarea,
    verify_task_ownership
)
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import time
from starlette.middleware.base import BaseHTTPMiddleware
import re
from jose import jwt, JWTError
import json
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Middleware para rate limiting
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests = {}
        self.login_requests = {}
        self.task_requests = {}
        
    async def dispatch(self, request: Request, call_next):
        # Rutas públicas que no requieren rate limiting
        public_paths = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health",
            "/invalid-json"  # Para pruebas de manejo de errores
        ]
        
        # Si la ruta es pública, permitir sin rate limiting
        if request.url.path in public_paths:
            return await call_next(request)
            
        # Obtener IP del cliente de forma segura
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
            
        now = time.time()
        window_start = now - 60  # Ventana de 60 segundos
        
        # Limpiar solicitudes antiguas
        for ip in list(self.requests.keys()):
            self.requests[ip] = [ts for ts in self.requests[ip] if ts > window_start]
            if not self.requests[ip]:
                del self.requests[ip]
                
        for ip in list(self.login_requests.keys()):
            self.login_requests[ip] = [ts for ts in self.login_requests[ip] if ts > window_start]
            if not self.login_requests[ip]:
                del self.login_requests[ip]
                
        for ip in list(self.task_requests.keys()):
            self.task_requests[ip] = [ts for ts in self.task_requests[ip] if ts > window_start]
            if not self.task_requests[ip]:
                del self.task_requests[ip]
                
        # Aplicar límites específicos para el endpoint de login
        if request.url.path == "/token":
            if client_ip not in self.login_requests:
                self.login_requests[client_ip] = []
            self.login_requests[client_ip].append(now)
            
            if len(self.login_requests[client_ip]) > settings.LOGIN_RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Demasiadas solicitudes"},
                    headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
                )
                
        # Aplicar límites específicos para endpoints de tareas
        elif request.url.path.startswith("/tareas"):
            if client_ip not in self.task_requests:
                self.task_requests[client_ip] = []
            self.task_requests[client_ip].append(now)
            
            if len(self.task_requests[client_ip]) > settings.TASK_RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Demasiadas solicitudes"},
                    headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
                )
                
        # Aplicar límite general para otras rutas
        else:
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            self.requests[client_ip].append(now)
            
            if len(self.requests[client_ip]) > settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Demasiadas solicitudes"},
                    headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
                )
                
        return await call_next(request)

# Middleware para autenticación
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next):
        # Permitir peticiones OPTIONS (preflight CORS) sin autenticación
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Lista de rutas públicas que no requieren autenticación
        public_paths = [
            "/register",
            "/login",
            "/token",
            "/refresh",
            "/logout",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/invalid-json",  # Para el test de manejo de errores
            "/password/requirements",
            "/password/check-strength",
            "/password/validate"
        ]
        
        # Si la ruta es pública, permitir el acceso sin autenticación
        if request.url.path in public_paths:
            return await call_next(request)
            
        # Obtener el token del header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "No se proporcionó token de acceso"},
                headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
            )
            
        token = auth_header.split(" ")[1]
        
        try:
            # Verificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = str(payload.get("sub", ""))
            if not email:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token de acceso inválido"},
                    headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
                )
                
            token_type = str(payload.get("type", ""))
            if token_type != "access":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token de acceso inválido"},
                    headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
                )
                
            # Obtener el usuario
            db = SessionLocal()
            try:
                user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Usuario no encontrado"},
                        headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
                    )
                    
                # Verificar si el usuario está activo usando el atributo directamente
                is_active = bool(db.query(models.Usuario.is_active).filter(models.Usuario.id == user.id).scalar())
                if not is_active:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Usuario inactivo"},
                        headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
                    )
                
                # Agregar el usuario a la solicitud
                request.state.user = user
                
                # Continuar con la solicitud
                response = await call_next(request)
                return response
            finally:
                db.close()
        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token de acceso inválido"},
                headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Error en autenticación: {str(e)}"},
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
            )

# Gestión del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación:
    - Crea tablas de la base de datos al inicio.
    - Cierra las conexiones de la base de datos al finalizar.
    """
    models.Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestión de tareas con autenticación JWT y refresh tokens"
)

# Manejadores de excepciones
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de errores de validación de solicitudes"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
    )

@app.exception_handler(json.JSONDecodeError)
async def json_decode_exception_handler(request: Request, exc: json.JSONDecodeError):
    """Manejador de errores de decodificación JSON"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "JSON inválido"},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejador de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
    )

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middlewares en orden correcto
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

def get_db():
    """Proporciona una sesión de base de datos por solicitud"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_not_found(item_name: str):
    """Levanta una excepción HTTP 404 para recursos no encontrados"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item_name.capitalize()} no encontrado(a)"
    )

def get_safe_id(obj: Any) -> int:
    """Extrae el ID de manera segura de un objeto SQLAlchemy"""
    return getattr(obj, 'id', 0)

# Endpoints de autenticación
@app.post(
    "/register",
    response_model=schemas.Usuario,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    tags=["Autenticación"]
)
def register(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    
    - Valida el formato del email
    - Verifica que la contraseña cumpla los requisitos mínimos
    - Verifica que el username sea único
    - Retorna los datos del usuario creado (sin contraseña)
    """
    return crud.create_usuario(db=db, usuario=usuario)

@app.post(
    "/token",
    response_model=schemas.Token,
    summary="Obtener token de acceso JWT (OAuth2 Password Flow)",
    tags=["Autenticación"]
)
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autenticación estándar OAuth2 Password Flow.
    Recibe username y password como x-www-form-urlencoded.
    """
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    is_active = getattr(user, "is_active", False)
    if not user or not is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos o usuario inactivo",
            headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
        )
    if not authenticate_user(db, form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
        )
    
    try:
        # Actualizar último login
        crud.update_last_login(db, user)
        
        # Crear tokens
        access_token = create_access_token(data={"sub": user.email, "type": "access", "user_id": user.id})
        refresh_token_jwt = create_refresh_token(user)
        
        # Guardar refresh token en la base de datos
        crud.create_refresh_token(
            db=db,
            usuario_id=get_safe_id(user),
            token=refresh_token_jwt
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_jwt,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        # Manejar errores de base de datos u otros errores
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el login: {str(e)}",
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
        )

@app.post(
    "/refresh",
    response_model=schemas.RefreshTokenResponse,
    summary="Refrescar token de acceso usando refresh token",
    tags=["Autenticación"]
)
def refresh_token(
    refresh_token: schemas.RefreshTokenCreate,
    db: Session = Depends(get_db)
):
    """
    Refresca el token de acceso usando un refresh token válido.
    
    - Verifica que el refresh token sea válido y no esté expirado
    - Genera un nuevo token de acceso
    - Retorna el nuevo token de acceso junto con el refresh token existente
    """
    db_token = crud.get_refresh_token(db, refresh_token.token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o expirado",
            headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
        )
    
    # Obtener usuario y crear nuevos tokens
    user = crud.get_usuario(db, get_safe_id(db_token.usuario))
    if not user or not bool(user.is_active):
        crud.revoke_refresh_token(db, refresh_token.token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"},
        )
    
    return create_tokens_for_user(user)

@app.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión y revocar refresh token",
    tags=["Autenticación"]
)
def logout(
    refresh_token: schemas.RefreshTokenCreate,
    db: Session = Depends(get_db)
):
    """
    Cierra la sesión del usuario y revoca el refresh token.
    
    - Revoca el refresh token proporcionado
    - No afecta a otros dispositivos/sesiones del usuario
    """
    crud.revoke_refresh_token(db, refresh_token.token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post(
    "/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar todas las sesiones del usuario",
    tags=["Autenticación"]
)
def logout_all(
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cierra todas las sesiones del usuario actual.
    
    - Revoca todos los refresh tokens del usuario
    - Requiere autenticación
    """
    crud.revoke_all_user_tokens(db, get_safe_id(current_user))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get(
    "/me",
    response_model=schemas.Usuario,
    summary="Obtener información del usuario actual",
    tags=["Autenticación"]
)
def read_users_me(current_user: models.Usuario = Depends(get_current_active_user)):
    """Retorna la información del usuario autenticado actualmente"""
    return current_user

# Endpoints de tareas
@app.post("/tareas", response_model=schemas.Tarea, status_code=status.HTTP_201_CREATED)
async def crear_tarea(
    tarea: schemas.TareaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear una nueva tarea"""
    try:
        # Convertir el ID del usuario a int de forma segura
        usuario_id = get_safe_id(current_user)
        nueva_tarea = crud.create_tarea(db=db, tarea=tarea, usuario_id=usuario_id)
        return nueva_tarea
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}",
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
        )

@app.get(
    "/tareas",
    response_model=schemas.TareaListResponse,
    summary="Listar tareas con filtros y paginación",
    tags=["Tareas"]
)
def listar_tareas(
    skip: int = 0,
    limit: int = 10,
    completado: Optional[bool] = None,
    prioridad: Optional[int] = None,
    buscar: Optional[str] = None,
    ordenar_por: str = "created_at",
    orden: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Lista las tareas del usuario con filtros y paginación.
    
    - Soporta filtrado por estado de completado y prioridad
    - Soporta búsqueda en título y descripción
    - Soporta ordenamiento por cualquier campo
    - Incluye información de paginación
    """
    try:
        tareas, total = crud.get_tareas(
            db=db,
            usuario_id=get_safe_id(current_user),
            skip=skip,
            limit=limit,
            completado=completado,
            prioridad=prioridad,
            buscar=buscar,
            ordenar_por=ordenar_por,
            orden=orden
        )
        
        # Calcular el número total de páginas
        total_pages = (total + limit - 1) // limit
        
        return {
            "items": tareas,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": total_pages
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar tareas: {str(e)}",
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
        )

def get_user_for_tarea(tarea_id: int):
    """Función auxiliar para obtener el usuario para una tarea específica"""
    async def get_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> models.Usuario:
        return await get_current_user_for_tarea(token=token, db=db, tarea_id=tarea_id)
    return get_user

@app.get("/tareas/{tarea_id}", response_model=schemas.Tarea)
async def get_tarea(
    tarea_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener una tarea por su ID"""
    # Si la tarea está en el estado de la solicitud, usarla
    if hasattr(request.state, "tarea"):
        return request.state.tarea
        
    # Si no está en el estado, buscarla en la base de datos
    usuario_id = get_safe_id(current_user)
    tarea = crud.get_tarea(db, tarea_id, usuario_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
        )
    return tarea

@app.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
async def update_tarea(
    tarea_id: int,
    tarea_update: schemas.TareaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar una tarea"""
    # Si la tarea está en el estado de la solicitud, usarla
    tarea = request.state.tarea if hasattr(request.state, "tarea") else None
    if not tarea:
        usuario_id = get_safe_id(current_user)
        tarea = crud.get_tarea(db, tarea_id, usuario_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
            )
            
    # Actualizar la tarea
    tarea_updated = crud.update_tarea(db, tarea, tarea_update)
    return tarea_updated

@app.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tarea(
    tarea_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar una tarea"""
    # Si la tarea está en el estado de la solicitud, usarla
    tarea = request.state.tarea if hasattr(request.state, "tarea") else None
    if not tarea:
        usuario_id = get_safe_id(current_user)
        tarea = crud.get_tarea(db, tarea_id, usuario_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}
            )
            
    # Eliminar la tarea
    crud.delete_tarea(db, tarea)
    return None

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Verificar estado del servicio",
    tags=["Sistema"]
)
def health_check(db: Session = Depends(get_db)):
    """
    Verifica el estado del servicio y la conexión a la base de datos.
    
    Retorna:
    - Estado del servicio
    - Versión de la API
    - Estado de la base de datos
    - Timestamp actual
    """
    try:
        # Verificar conexión a la base de datos
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get(
    "/password/requirements",
    response_model=schemas.PasswordRequirements,
    summary="Obtener requisitos de contraseña",
    tags=["Autenticación"]
)
def get_password_requirements():
    """
    Retorna los requisitos de contraseña para mostrar al usuario.
    
    Útil para formularios de registro y cambio de contraseña.
    """
    from app.password_validator import get_password_requirements
    return get_password_requirements()

@app.post(
    "/password/check-strength",
    response_model=schemas.PasswordStrengthAnalysis,
    summary="Analizar fortaleza de contraseña",
    tags=["Autenticación"]
)
def check_password_strength(password_data: schemas.PasswordCheck):
    """
    Analiza la fortaleza de una contraseña sin validarla.
    
    Útil para mostrar feedback en tiempo real al usuario.
    
    Args:
        password_data: Datos de la contraseña a analizar
        
    Returns:
        dict: Análisis detallado de la fortaleza
    """
    from app.password_validator import check_password_strength
    return check_password_strength(password_data.password)

@app.post(
    "/password/validate",
    response_model=schemas.PasswordValidationResponse,
    summary="Validar contraseña",
    tags=["Autenticación"]
)
def validate_password(password_data: schemas.PasswordCheck):
    """
    Valida una contraseña contra todos los requisitos de seguridad.
    
    Args:
        password_data: Datos de la contraseña a validar
        
    Returns:
        dict: Resultado de la validación con mensajes de error
    """
    from app.password_validator import validate_password_strength
    
    is_valid, error_message = validate_password_strength(password_data.password)
    
    return {
        "is_valid": is_valid,
        "error_message": error_message if not is_valid else None
    }