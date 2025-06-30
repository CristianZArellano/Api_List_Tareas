"""
Configuración de pruebas para la aplicación de Lista de Tareas
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.main import get_db
from app.config import settings

# Configuración de base de datos SQLite en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Engine y sessionmaker para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Sesión de base de datos para cada test"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba que usa la sesión de base de datos del test"""
    def override_get_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise
    
    # Deshabilitar rate limiting para pruebas usando un valor alto
    settings.RATE_LIMIT_PER_MINUTE = 1000000
    settings.LOGIN_RATE_LIMIT_PER_MINUTE = 1000000
    settings.TASK_RATE_LIMIT_PER_MINUTE = 1000000
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function", autouse=True)
def clean_db(db_session):
    """Limpia la base de datos antes de cada test"""
    # Limpiar todas las tablas antes del test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    yield

@pytest.fixture
def test_user_data():
    """Datos de usuario de prueba"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePassX9!"
    }

@pytest.fixture
def test_user_data_2():
    """Datos de segundo usuario de prueba"""
    return {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "StrongPassY8!"
    }

@pytest.fixture
def test_tarea_data():
    """Datos de tarea de prueba"""
    return {
        "titulo": "Tarea de prueba",
        "descripcion": "Descripción de la tarea de prueba",
        "completado": False,
        "prioridad": 1
    }

@pytest.fixture
def test_tarea_data_2():
    """Datos de segunda tarea de prueba"""
    return {
        "titulo": "Segunda tarea",
        "descripcion": "Otra tarea para pruebas",
        "completado": True,
        "prioridad": 2
    }

@pytest.fixture
def auth_headers(client, clean_db, test_user_data):
    """Fixture para obtener headers de autenticación"""
    try:
        # Registrar usuario
        register_response = client.post("/register", json=test_user_data)
        if register_response.status_code not in [201, 422]:  # 422 si ya existe
            print(f"Error en registro: {register_response.status_code} - {register_response.text}")
        
        # Login estándar OAuth2
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/token", data=login_data)
        
        if login_response.status_code != 200:
            print(f"Error en login: {login_response.status_code} - {login_response.text}")
            # Si falla, intentar registrar de nuevo con datos diferentes
            test_user_data_alt = test_user_data.copy()
            test_user_data_alt["email"] = "alt@example.com"
            test_user_data_alt["username"] = "altuser"
            client.post("/register", json=test_user_data_alt)
            login_data["username"] = test_user_data_alt["email"]
            login_data["password"] = test_user_data_alt["password"]
            login_response = client.post("/token", data=login_data)
        
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Error en auth_headers fixture: {e}")
        # Retornar headers vacíos si falla
        return {"Authorization": f"Bearer invalid_token"} 