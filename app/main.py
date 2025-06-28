from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, crud
from app.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional # Union is not explicitly needed here

# ---
# 1. Gestión mejorada del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación:
    - Crea tablas de la base de datos al inicio.
    - Cierra las conexiones de la base de datos al finalizar.
    """
    # Crear tablas al iniciar, si no existen
    models.Base.metadata.create_all(bind=engine)
    yield
    # Cerrar conexiones al finalizar para liberar recursos
    engine.dispose()

app = FastAPI(lifespan=lifespan, title="API de Tareas", version="1.0.0")

# ---
# 2. Configuración de CORS para comunicación con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (ajustar para producción)
    allow_credentials=True, # Permite el envío de cookies y credenciales
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los encabezados en las solicitudes
)

# ---
# 3. Dependencia de base de datos optimizada
def get_db():
    """
    Proporciona una sesión de base de datos por solicitud.
    Asegura que la sesión se cierre correctamente después de cada uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---
# 4. Manejo centralizado de errores para recursos no encontrados
def handle_not_found(item_name: str):
    """
    Levanta una excepción HTTP 404 para indicar que un recurso no fue encontrado.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item_name.capitalize()} no encontrado(a)"
    )

# ---
# 5. Crear una tarea
@app.post(
    "/tareas",
    response_model=schemas.Tarea,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva tarea en la base de datos",
    tags=["Tareas"]
)
def crear_tarea(tarea: schemas.TareaCrear, db: Session = Depends(get_db)):
    """
    Crea una nueva tarea con los datos proporcionados.
    Retorna la tarea creada, incluyendo su ID.
    """
    # El manejo de excepciones específicas de DB ya está en crud.py
    # Aquí solo necesitamos preocuparnos por el 400 si la validación Pydantic falla,
    # pero FastAPI ya lo maneja automáticamente.
    # El `try-except` general aquí podría ocultar errores específicos.
    # Es mejor dejar que las excepciones de crud.py se propaguen si son HTTPException.
    return crud.create_tarea(db=db, tarea=tarea)


# ---
# 6. Listar tareas
@app.get(
    "/tareas",
    response_model=list[schemas.Tarea],
    summary="Obtener una lista de todas las tareas existentes",
    tags=["Tareas"]
)
def listar_tareas(
    skip: int = 0,
    limit: int = 100,
    completado: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Recupera una lista de tareas.
    Puedes paginar los resultados usando `skip` y `limit`,
    y filtrar por el estado de `completado`.
    """
    return crud.get_tareas(
        db=db,
        skip=skip,
        limit=limit,
        completado=completado
    )

# ---
# 7. Obtener tarea por ID
@app.get(
    "/tareas/{tarea_id}",
    response_model=schemas.Tarea,
    summary="Obtener los detalles de una tarea específica por su ID",
    tags=["Tareas"]
)
def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """
    Retorna una tarea específica basada en su ID.
    Lanza un error 404 si la tarea no se encuentra.
    """
    if tarea := crud.get_tarea(db=db, tarea_id=tarea_id):
        return tarea
    handle_not_found("tarea")

# ---
# 8. Actualizar tarea
@app.put(
    "/tareas/{tarea_id}",
    response_model=schemas.Tarea,
    summary="Actualizar parcial o totalmente una tarea existente",
    tags=["Tareas"]
)
def actualizar_tarea(
    tarea_id: int,
    datos: schemas.TareaActualizar,
    db: Session = Depends(get_db)
):
    """
    Actualiza una tarea existente identificada por su ID con los datos proporcionados.
    Los campos no incluidos en la solicitud no serán modificados.
    Lanza un error 404 si la tarea no se encuentra.
    """
    tarea = crud.update_tarea(db=db, tarea_id=tarea_id, datos=datos)
    if not tarea:
        handle_not_found("tarea")
    return tarea

# ---
# 9. Eliminar tarea
@app.delete(
    "/tareas/{tarea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una tarea de la base de datos",
    tags=["Tareas"]
)
def eliminar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """
    Elimina una tarea existente por su ID.
    Retorna un estado 204 No Content en caso de éxito.
    Lanza un error 404 si la tarea no se encuentra.
    """
    # Verificar primero si la tarea existe para dar un 404 claro
    tarea_existente = crud.get_tarea(db=db, tarea_id=tarea_id)
    if not tarea_existente:
        handle_not_found("tarea")

    # Si existe, proceder a eliminarla
    crud.delete_tarea(db=db, tarea_id=tarea_id)
    # FastAPI automáticamente retornará 204 si no hay return
    # después de un `status_code` configurado para 204.


# ---
# 10. Endpoint adicional para estado del servicio
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Verificar el estado del servicio y la conexión a la base de datos",
    tags=["Sistema"]
)
def health_check(db: Session = Depends(get_db)):
    """
    Verifica que la aplicación esté funcionando y pueda conectarse a la base de datos.
    """
    try:
        # Ejecutar una consulta simple para verificar la conexión a la base de datos
        
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # En caso de error de conexión a la base de datos
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de conexión a la base de datos: {str(e)}"
        )