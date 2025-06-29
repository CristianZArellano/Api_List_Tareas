import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base
from app.main import get_db
from app.config import settings

# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Engine de base de datos para pruebas"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Sesión de base de datos para cada test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba con base de datos limpia"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Deshabilitar rate limiting para pruebas usando un valor alto
    settings.RATE_LIMIT_PER_MINUTE = 1000000
    settings.LOGIN_RATE_LIMIT_PER_MINUTE = 1000000
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def clean_db(db_session):
    """Limpia la base de datos después de cada test"""
    yield
    # Limpiar todas las tablas
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit() 