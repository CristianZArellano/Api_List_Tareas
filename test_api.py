import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, get_db
from app.models import Usuario, Tarea
from app.security import create_access_token
from datetime import datetime, timedelta
from app.database import Base
from app.config import settings
import time

# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override de la dependencia de base de datos para pruebas"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplicar el override
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Datos de prueba
test_user_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
}

test_user_data_2 = {
    "email": "test2@example.com",
    "username": "testuser2",
    "password": "testpassword123"
}

test_tarea_data = {
    "titulo": "Tarea de prueba",
    "descripcion": "Descripción de la tarea de prueba",
    "completado": False,
    "prioridad": 1
}

test_tarea_data_2 = {
    "titulo": "Segunda tarea",
    "descripcion": "Otra tarea para pruebas",
    "completado": True,
    "prioridad": 2
}

@pytest.fixture(scope="function")
def auth_headers(client, clean_db):
    """Fixture para obtener headers de autenticación"""
    # Registrar usuario
    client.post("/register", json=test_user_data)
    
    # Login con device_info
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
        "device_info": "Test Device"
    }
    login_response = client.post("/login", json=login_data)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    """Tests para endpoints de autenticación"""
    
    def test_register_user_success(self, client, clean_db):
        """Test registro exitoso de usuario"""
        response = client.post("/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "password" not in data
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_register_user_duplicate_email(self, client, clean_db):
        """Test registro con email duplicado"""
        # Registrar primer usuario
        client.post("/register", json=test_user_data)
        
        # Intentar registrar con el mismo email
        duplicate_user = test_user_data.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/register", json=duplicate_user)
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]
    
    def test_register_user_duplicate_username(self, client, clean_db):
        """Test registro con username duplicado"""
        # Registrar primer usuario
        client.post("/register", json=test_user_data)
        
        # Intentar registrar con el mismo username
        duplicate_user = test_user_data.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/register", json=duplicate_user)
        assert response.status_code == 400
        assert "nombre de usuario ya está en uso" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client, clean_db):
        """Test registro con email inválido"""
        invalid_user = test_user_data.copy()
        invalid_user["email"] = "invalid-email"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422
    
    def test_register_user_short_password(self, client, clean_db):
        """Test registro con contraseña muy corta"""
        invalid_user = test_user_data.copy()
        invalid_user["password"] = "123"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422
    
    def test_register_user_short_username(self, client, clean_db):
        """Test registro con username muy corto"""
        invalid_user = test_user_data.copy()
        invalid_user["username"] = "ab"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422
    
    def test_login_success(self, client, clean_db):
        """Test login exitoso"""
        # Registrar usuario primero
        client.post("/register", json=test_user_data)
        time.sleep(1)  # Esperar para evitar rate limit
        
        # Hacer login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "device_info": "Test Device"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, clean_db):
        """Test login con credenciales inválidas"""
        time.sleep(1)  # Esperar para evitar rate limit
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
            "device_info": "Test Device"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]
    
    def test_me_endpoint_with_token(self, client, clean_db):
        """Test endpoint /me con token válido"""
        # Registrar y hacer login
        client.post("/register", json=test_user_data)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "device_info": "Test Device"
        })
        token = login_response.json()["access_token"]
        
        # Usar token para acceder a /me
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    def test_me_endpoint_without_token(self, client, clean_db):
        """Test endpoint /me sin token"""
        response = client.get("/me")
        assert response.status_code == 401
    
    def test_me_endpoint_invalid_token(self, client, clean_db):
        """Test endpoint /me con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
    
    def test_login_with_device_info(self, client, clean_db):
        """Test login con información del dispositivo"""
        # Registrar usuario
        client.post("/register", json=test_user_data)
        time.sleep(1)  # Esperar para evitar rate limit
        
        # Login con device_info
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "device_info": "Test Device"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_success(self, client, clean_db):
        """Test refresh token exitoso"""
        # Registrar y hacer login
        client.post("/register", json=test_user_data)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "device_info": "Test Device"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Usar refresh token
        response = client.post("/refresh", json={"token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client, clean_db):
        """Test refresh token inválido"""
        response = client.post("/refresh", json={"token": "invalid_token"})
        assert response.status_code == 401
        assert "Token de refresco inválido o expirado" in response.json()["detail"]
    
    def test_logout_success(self, client, clean_db):
        """Test logout exitoso"""
        # Registrar y hacer login
        client.post("/register", json=test_user_data)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "device_info": "Test Device"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        response = client.post("/logout", json={"token": refresh_token})
        assert response.status_code == 204
        
        # Intentar usar el refresh token después de logout
        refresh_response = client.post("/refresh", json={"token": refresh_token})
        assert refresh_response.status_code == 401
    
    def test_logout_all_success(self, client, auth_headers, clean_db):
        """Test logout de todas las sesiones"""
        response = client.post("/logout/all", headers=auth_headers)
        assert response.status_code == 204
    
    def test_rate_limit_login(self, client, clean_db):
        """Test rate limit en endpoint de login"""
        # Configurar límites bajos para la prueba
        original_login_limit = settings.LOGIN_RATE_LIMIT_PER_MINUTE
        settings.LOGIN_RATE_LIMIT_PER_MINUTE = 5
        
        try:
            # Registrar usuario
            client.post("/register", json=test_user_data)
            
            # Intentar login múltiples veces con credenciales correctas
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"],  # Usar contraseña correcta
                "device_info": "Test Device"
            }
            
            # Configurar headers para simular una IP consistente
            headers = {"X-Forwarded-For": "127.0.0.1"}
            
            responses = []
            # Hacer 7 intentos (el límite es 5 por minuto)
            for i in range(7):
                print(f"\nIntento {i+1} de login...")
                response = client.post("/login", json=login_data, headers=headers)
                status_code = response.status_code
                responses.append(status_code)
                print(f"Respuesta: {status_code}")
                if status_code == 500:
                    print(f"Error 500: {response.text}")
                if status_code == 429:
                    break
                time.sleep(0.1)  # Pequeña pausa entre intentos
            
            print(f"\nCódigos de respuesta recibidos: {responses}")
            
            # Verificar que al menos un intento fue exitoso (200) y eventualmente obtuvimos 429
            assert 200 in responses, "Al menos un intento de login debería ser exitoso"
            assert 429 in responses, "Debería haber alcanzado el límite de intentos"
            assert response.status_code == 429
            assert "Demasiadas solicitudes" in response.json()["detail"]
        finally:
            # Restaurar el límite original
            settings.LOGIN_RATE_LIMIT_PER_MINUTE = original_login_limit

class TestTareas:
    """Tests para endpoints de tareas"""
    
    def test_create_tarea_success(self, client, auth_headers, clean_db):
        """Test creación exitosa de tarea"""
        response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == test_tarea_data["titulo"]
        assert data["descripcion"] == test_tarea_data["descripcion"]
        assert data["completado"] == test_tarea_data["completado"]
        assert "id" in data
        assert "created_at" in data
        assert "usuario_id" in data
    
    def test_create_tarea_without_auth(self, client, clean_db):
        """Test creación de tarea sin autenticación"""
        response = client.post("/tareas", json=test_tarea_data)
        assert response.status_code == 401
    
    def test_create_tarea_invalid_data(self, client, auth_headers, clean_db):
        """Test creación de tarea con datos inválidos"""
        invalid_tarea = {"titulo": "", "descripcion": "test"}
        response = client.post("/tareas", json=invalid_tarea, headers=auth_headers)
        assert response.status_code == 422
    
    def test_get_tareas_empty(self, client, auth_headers, clean_db):
        """Test obtener lista de tareas vacía"""
        response = client.get("/tareas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0
        assert data["total"] == 0
    
    def test_get_tareas_with_data(self, client, auth_headers, clean_db):
        """Test obtener lista de tareas con datos"""
        # Crear algunas tareas
        client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        client.post("/tareas", json=test_tarea_data_2, headers=auth_headers)
        
        response = client.get("/tareas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["titulo"] == test_tarea_data["titulo"]
        assert data["items"][1]["titulo"] == test_tarea_data_2["titulo"]
    
    def test_get_tareas_with_pagination(self, client, auth_headers, clean_db):
        """Test obtener tareas con paginación"""
        # Crear múltiples tareas
        for i in range(5):
            tarea = test_tarea_data.copy()
            tarea["titulo"] = f"Tarea {i}"
            client.post("/tareas", json=tarea, headers=auth_headers)
        
        # Obtener solo 3 tareas
        response = client.get("/tareas?limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 3
        assert data["pages"] == 2
    
    def test_get_tareas_with_filter(self, client, auth_headers, clean_db):
        """Test obtener tareas con filtro de completado"""
        # Crear tareas con diferentes estados
        client.post("/tareas", json=test_tarea_data, headers=auth_headers)  # No completada
        client.post("/tareas", json=test_tarea_data_2, headers=auth_headers)  # Completada
        
        # Filtrar completadas
        response = client.get("/tareas?completado=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["completado"] is True
    
    def test_get_tarea_by_id_success(self, client, auth_headers, clean_db):
        """Test obtener tarea por ID"""
        # Crear tarea
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Obtener tarea
        response = client.get(f"/tareas/{tarea_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tarea_id
        assert data["titulo"] == test_tarea_data["titulo"]
    
    def test_get_tarea_by_id_not_found(self, client, auth_headers, clean_db):
        """Test obtener tarea inexistente"""
        response = client.get("/tareas/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_tarea_by_id_other_user(self, client, auth_headers, clean_db):
        """Test obtener tarea de otro usuario"""
        # Crear tarea con primer usuario
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Registrar segundo usuario y obtener token
        client.post("/register", json=test_user_data_2)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"],
            "device_info": "Test Device 2"
        })
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Intentar obtener tarea del primer usuario
        response = client.get(f"/tareas/{tarea_id}", headers=other_headers)
        assert response.status_code == 401
    
    def test_update_tarea_success(self, client, auth_headers, clean_db):
        """Test actualizar tarea exitosamente"""
        # Crear tarea
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Actualizar tarea
        update_data = {"titulo": "Título actualizado", "completado": True}
        response = client.put(f"/tareas/{tarea_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == update_data["titulo"]
        assert data["completado"] == update_data["completado"]
        assert data["descripcion"] == test_tarea_data["descripcion"]  # No cambia
    
    def test_update_tarea_not_found(self, client, auth_headers, clean_db):
        """Test actualizar tarea inexistente"""
        update_data = {"titulo": "Nuevo título"}
        response = client.put("/tareas/999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_tarea_other_user(self, client, auth_headers, clean_db):
        """Test actualizar tarea de otro usuario"""
        # Crear tarea con primer usuario
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Registrar segundo usuario y obtener token
        client.post("/register", json=test_user_data_2)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"],
            "device_info": "Test Device 2"
        })
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Intentar actualizar tarea del primer usuario
        update_data = {"titulo": "Intento de actualización"}
        response = client.put(f"/tareas/{tarea_id}", json=update_data, headers=other_headers)
        assert response.status_code == 401
    
    def test_delete_tarea_success(self, client, auth_headers, clean_db):
        """Test eliminar tarea exitosamente"""
        # Crear tarea
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Eliminar tarea
        response = client.delete(f"/tareas/{tarea_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verificar que la tarea fue eliminada
        get_response = client.get(f"/tareas/{tarea_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_tarea_not_found(self, client, auth_headers, clean_db):
        """Test eliminar tarea inexistente"""
        response = client.delete("/tareas/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_tarea_other_user(self, client, auth_headers, clean_db):
        """Test eliminar tarea de otro usuario"""
        # Crear tarea con primer usuario
        create_response = client.post("/tareas", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Registrar segundo usuario y obtener token
        client.post("/register", json=test_user_data_2)
        time.sleep(1)  # Esperar para evitar rate limit
        login_response = client.post("/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"],
            "device_info": "Test Device 2"
        })
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Intentar eliminar tarea del primer usuario
        response = client.delete(f"/tareas/{tarea_id}", headers=other_headers)
        assert response.status_code == 401
    
    def test_get_tareas_with_metadata(self, client, auth_headers, clean_db):
        """Test obtener tareas con metadata de paginación"""
        # Crear múltiples tareas
        for i in range(15):
            tarea = test_tarea_data.copy()
            tarea["titulo"] = f"Tarea {i}"
            client.post("/tareas", json=tarea, headers=auth_headers)
        
        # Obtener página de tareas
        response = client.get("/tareas?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["page"] == 2
        assert data["size"] == 5
        assert data["pages"] == 3
    
    def test_get_tareas_with_filters(self, client, auth_headers, clean_db):
        """Test obtener tareas con filtros avanzados"""
        # Crear tareas con diferentes estados y prioridades
        tareas = [
            {"titulo": "Alta prioridad", "descripcion": "Test", "prioridad": 3, "completado": False},
            {"titulo": "Media prioridad", "descripcion": "Test", "prioridad": 2, "completado": True},
            {"titulo": "Baja prioridad", "descripcion": "Test", "prioridad": 1, "completado": False}
        ]
        
        for tarea in tareas:
            client.post("/tareas", json=tarea, headers=auth_headers)
        
        # Filtrar por prioridad
        response = client.get("/tareas?prioridad=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["titulo"] == "Alta prioridad"
        
        # Filtrar por completado
        response = client.get("/tareas?completado=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["titulo"] == "Media prioridad"
        
        # Buscar por texto
        response = client.get("/tareas?buscar=alta", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["titulo"] == "Alta prioridad"
        
        # Ordenar por prioridad descendente
        response = client.get("/tareas?ordenar_por=prioridad&orden=desc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["items"][0]["prioridad"] == 3
    
    def test_rate_limit_tareas(self, client, auth_headers, clean_db):
        """Test rate limit en endpoints de tareas"""
        # Establecer un límite más bajo para la prueba
        original_limit = settings.TASK_RATE_LIMIT_PER_MINUTE
        settings.TASK_RATE_LIMIT_PER_MINUTE = 3  # Límite bajo para la prueba
        
        try:
            # Configurar headers para simular una IP consistente
            headers = auth_headers.copy()
            headers["X-Forwarded-For"] = "192.168.1.100"
            
            # Hacer una serie de solicitudes rápidas
            responses = []
            for i in range(6):  # Hacer el doble de solicitudes que el límite
                response = client.get("/tareas", headers=headers)
                responses.append(response)
                print(f"Request {i+1}: {response.status_code}")
            
            # Verificar que las primeras solicitudes fueron exitosas
            successful_requests = [r for r in responses if r.status_code == 200]
            failed_requests = [r for r in responses if r.status_code == 429]
            
            print(f"Successful requests: {len(successful_requests)}")
            print(f"Failed requests: {len(failed_requests)}")
            
            assert len(successful_requests) > 0, "Deberían haber solicitudes exitosas"
            assert len(failed_requests) > 0, "Deberían haber solicitudes fallidas por rate limit"
            
            # Verificar el mensaje de error
            for failed_request in failed_requests:
                assert "Demasiadas solicitudes" in failed_request.json()["detail"]
                
        finally:
            # Restaurar el límite original
            settings.TASK_RATE_LIMIT_PER_MINUTE = original_limit

class TestHealthCheck:
    """Tests para el endpoint de health check"""
    
    def test_health_check_response(self, client, clean_db):
        """Test respuesta detallada del health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "version" in data
        assert data["database"] == "healthy"
        assert "timestamp" in data
        
        # Verificar formato ISO de timestamp
        datetime.fromisoformat(data["timestamp"])

class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def test_invalid_json(self, client, clean_db):
        """Test con JSON inválido"""
        response = client.post(
            "/tareas",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401
    
    def test_missing_required_fields(self, client, auth_headers, clean_db):
        """Test con campos requeridos faltantes"""
        response = client.post("/tareas", json={}, headers=auth_headers)
        assert response.status_code == 422
    
    def test_invalid_tarea_id_format(self, client, auth_headers, clean_db):
        """Test con ID de tarea en formato inválido"""
        response = client.get("/tareas/abc", headers=auth_headers)
        assert response.status_code == 422
    
    def test_invalid_sort_field(self, client, auth_headers, clean_db):
        """Test ordenamiento por campo inválido"""
        response = client.get("/tareas?ordenar_por=campo_invalido", headers=auth_headers)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 