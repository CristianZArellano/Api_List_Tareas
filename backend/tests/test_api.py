"""
Pruebas unitarias para la API de Lista de Tareas
"""
import pytest
import time
from fastapi.testclient import TestClient

# Datos de usuario de prueba actualizados
test_user_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassX9!"
}

test_user_data_2 = {
    "email": "test2@example.com", 
    "username": "testuser2",
    "password": "StrongPassY8!"
}

@pytest.mark.api
@pytest.mark.unit
class TestAuthentication:
    """Pruebas para endpoints de autenticación"""

    def test_register_user_success(self, client, clean_db, test_user_data):
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

    def test_register_user_duplicate_email(self, client, clean_db, test_user_data):
        """Test registro con email duplicado"""
        # Registrar primer usuario
        client.post("/register", json=test_user_data)
        
        # Intentar registrar con el mismo email
        duplicate_user = test_user_data.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/register", json=duplicate_user)
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]

    def test_register_user_duplicate_username(self, client, clean_db, test_user_data):
        """Test registro con username duplicado"""
        # Registrar primer usuario
        client.post("/register", json=test_user_data)
        
        # Intentar registrar con el mismo username
        duplicate_user = test_user_data.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/register", json=duplicate_user)
        assert response.status_code == 400
        assert "nombre de usuario ya está en uso" in response.json()["detail"]

    def test_register_user_invalid_email(self, client, clean_db, test_user_data):
        """Test registro con email inválido"""
        invalid_user = test_user_data.copy()
        invalid_user["email"] = "invalid-email"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422

    def test_register_user_short_password(self, client, clean_db, test_user_data):
        """Test registro con contraseña muy corta"""
        invalid_user = test_user_data.copy()
        invalid_user["password"] = "123"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422

    def test_register_user_short_username(self, client, clean_db, test_user_data):
        """Test registro con username muy corto"""
        invalid_user = test_user_data.copy()
        invalid_user["username"] = "ab"
        response = client.post("/register", json=invalid_user)
        assert response.status_code == 422

    def test_login_success(self, client, clean_db, test_user_data):
        """Test login exitoso"""
        # Registrar usuario primero
        client.post("/register", json=test_user_data)
        time.sleep(0.1)  # Pequeña pausa para evitar rate limit
        
        # Hacer login estándar OAuth2
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, clean_db):
        """Test login con credenciales inválidas"""
        time.sleep(0.1)  # Pequeña pausa para evitar rate limit
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401

    def test_me_endpoint_with_token(self, client, clean_db, test_user_data):
        """Test endpoint /me con token válido"""
        # Registrar y hacer login
        client.post("/register", json=test_user_data)
        time.sleep(0.1)  # Pequeña pausa para evitar rate limit
        
        login_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Usar el token para acceder al endpoint /me
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/me", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == test_user_data["email"]
        assert user_data["username"] == test_user_data["username"]

    def test_me_endpoint_without_token(self, client, clean_db):
        """Test endpoint /me sin token"""
        response = client.get("/me")
        assert response.status_code == 401

    def test_me_endpoint_invalid_token(self, client, clean_db):
        """Test endpoint /me con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 401

    def test_refresh_token_success(self, client, clean_db, test_user_data):
        """Test refresh token exitoso"""
        client.post("/register", json=test_user_data)
        time.sleep(0.1)
        login_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        refresh_token = login_response.json()["refresh_token"]
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

    def test_logout_success(self, client, clean_db, test_user_data):
        """Test logout exitoso"""
        client.post("/register", json=test_user_data)
        time.sleep(0.1)
        login_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        refresh_token = login_response.json()["refresh_token"]
        response = client.post("/logout", json={"token": refresh_token})
        assert response.status_code == 204

    def test_logout_all_success(self, client, auth_headers):
        """Test logout all exitoso"""
        response = client.post("/logout/all", headers=auth_headers)
        assert response.status_code == 204

    def test_rate_limit_login(self, client, clean_db, test_user_data):
        """Test rate limiting en login"""
        # Registrar usuario
        client.post("/register", json=test_user_data)
        
        # Intentar múltiples logins rápidamente
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        # Los primeros intentos deberían funcionar
        for _ in range(5):
            response = client.post("/token", data=login_data)
            assert response.status_code in [200, 429]  # 200 OK o 429 Rate Limited


@pytest.mark.api
@pytest.mark.unit
class TestTareas:
    """Pruebas para endpoints de tareas"""

    def test_create_tarea_success(self, client, auth_headers, clean_db, test_tarea_data):
        """Test creación exitosa de tarea"""
        response = client.post("/tareas/", json=test_tarea_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == test_tarea_data["titulo"]
        assert data["descripcion"] == test_tarea_data["descripcion"]
        assert data["completado"] == test_tarea_data["completado"]
        assert data["prioridad"] == test_tarea_data["prioridad"]
        assert "id" in data
        assert "created_at" in data

    def test_create_tarea_without_auth(self, client, clean_db, test_tarea_data):
        """Test creación de tarea sin autenticación"""
        response = client.post("/tareas/", json=test_tarea_data)
        assert response.status_code == 401

    def test_create_tarea_invalid_data(self, client, auth_headers, clean_db):
        """Test creación de tarea con datos inválidos"""
        invalid_tarea = {"titulo": ""}  # Sin descripción requerida
        response = client.post("/tareas/", json=invalid_tarea, headers=auth_headers)
        assert response.status_code == 422

    def test_get_tareas_empty(self, client, auth_headers, clean_db):
        """Test obtener tareas cuando no hay ninguna"""
        response = client.get("/tareas/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_tareas_with_data(self, client, auth_headers, clean_db, test_tarea_data):
        """Test obtener tareas con datos"""
        # Crear tarea
        client.post("/tareas/", json=test_tarea_data, headers=auth_headers)
        
        # Obtener tareas
        response = client.get("/tareas/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["titulo"] == test_tarea_data["titulo"]

    def test_get_tareas_with_pagination(self, client, auth_headers, clean_db, test_tarea_data):
        """Test paginación de tareas"""
        # Crear múltiples tareas
        for i in range(5):
            tarea = test_tarea_data.copy()
            tarea["titulo"] = f"Tarea {i+1}"
            client.post("/tareas/", json=tarea, headers=auth_headers)
        
        # Obtener primera página
        response = client.get("/tareas/?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    def test_get_tareas_with_filter(self, client, auth_headers, clean_db, test_tarea_data):
        """Test filtrado de tareas"""
        # Crear tarea completada
        completed_tarea = test_tarea_data.copy()
        completed_tarea["completado"] = True
        client.post("/tareas/", json=completed_tarea, headers=auth_headers)
        
        # Filtrar por completado
        response = client.get("/tareas/?completado=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["completado"] is True

    def test_get_tarea_by_id_success(self, client, auth_headers, clean_db, test_tarea_data):
        """Test obtener tarea por ID"""
        # Crear tarea
        create_response = client.post("/tareas/", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Obtener tarea por ID
        response = client.get(f"/tareas/{tarea_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tarea_id
        assert data["titulo"] == test_tarea_data["titulo"]

    def test_get_tarea_by_id_not_found(self, client, auth_headers, clean_db):
        """Test obtener tarea inexistente"""
        response = client.get("/tareas/999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_tarea_by_id_other_user(self, client, clean_db, test_user_data, test_user_data_2, test_tarea_data):
        """Test obtener tarea de otro usuario"""
        # Registrar dos usuarios
        client.post("/register", json=test_user_data)
        client.post("/register", json=test_user_data_2)
        
        # Login del primer usuario y crear tarea
        time.sleep(0.1)
        login1_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        tarea_response = client.post("/tareas", json=test_tarea_data, headers=headers1)
        tarea_id = tarea_response.json()["id"]
        
        # Login del segundo usuario
        time.sleep(0.1)
        login2_response = client.post("/token", data={
            "username": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Intentar acceder a la tarea del primer usuario
        response = client.get(f"/tareas/{tarea_id}", headers=headers2)
        assert response.status_code == 401

    def test_update_tarea_success(self, client, auth_headers, clean_db, test_tarea_data):
        """Test actualización exitosa de tarea"""
        # Crear tarea
        create_response = client.post("/tareas/", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Actualizar tarea
        update_data = {"titulo": "Tarea actualizada", "completado": True}
        response = client.put(f"/tareas/{tarea_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Tarea actualizada"
        assert data["completado"] is True

    def test_update_tarea_not_found(self, client, auth_headers, clean_db):
        """Test actualización de tarea inexistente"""
        response = client.put("/tareas/999", json={"titulo": "Nuevo título"}, headers=auth_headers)
        assert response.status_code == 404

    def test_update_tarea_other_user(self, client, clean_db, test_user_data, test_user_data_2, test_tarea_data):
        """Test actualizar tarea de otro usuario"""
        # Registrar dos usuarios
        client.post("/register", json=test_user_data)
        client.post("/register", json=test_user_data_2)
        
        # Login del primer usuario y crear tarea
        time.sleep(0.1)
        login1_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        tarea_response = client.post("/tareas", json=test_tarea_data, headers=headers1)
        tarea_id = tarea_response.json()["id"]
        
        # Login del segundo usuario
        time.sleep(0.1)
        login2_response = client.post("/token", data={
            "username": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Intentar actualizar la tarea del primer usuario
        update_data = {"titulo": "Tarea Actualizada por Otro Usuario"}
        response = client.put(f"/tareas/{tarea_id}", json=update_data, headers=headers2)
        assert response.status_code == 401

    def test_delete_tarea_success(self, client, auth_headers, clean_db, test_tarea_data):
        """Test eliminación exitosa de tarea"""
        # Crear tarea
        create_response = client.post("/tareas/", json=test_tarea_data, headers=auth_headers)
        tarea_id = create_response.json()["id"]
        
        # Eliminar tarea
        response = client.delete(f"/tareas/{tarea_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verificar que la tarea fue eliminada
        get_response = client.get(f"/tareas/{tarea_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_tarea_not_found(self, client, auth_headers, clean_db):
        """Test eliminación de tarea inexistente"""
        response = client.delete("/tareas/999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_tarea_other_user(self, client, clean_db, test_user_data, test_user_data_2, test_tarea_data):
        """Test eliminar tarea de otro usuario"""
        # Registrar dos usuarios
        client.post("/register", json=test_user_data)
        client.post("/register", json=test_user_data_2)
        
        # Login del primer usuario y crear tarea
        time.sleep(0.1)
        login1_response = client.post("/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        tarea_response = client.post("/tareas", json=test_tarea_data, headers=headers1)
        tarea_id = tarea_response.json()["id"]
        
        # Login del segundo usuario
        time.sleep(0.1)
        login2_response = client.post("/token", data={
            "username": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Intentar eliminar la tarea del primer usuario
        response = client.delete(f"/tareas/{tarea_id}", headers=headers2)
        assert response.status_code == 401

    def test_get_tareas_with_metadata(self, client, auth_headers, test_tarea_data):
        """Test obtener tareas con metadatos de paginación"""
        # Crear algunas tareas
        for i in range(3):
            tarea_data = test_tarea_data.copy()
            tarea_data["titulo"] = f"Tarea {i+1}"
            tarea_data["completado"] = i % 2 == 0
            client.post("/tareas", json=tarea_data, headers=auth_headers)
        
        # Obtener tareas con paginación
        response = client.get("/tareas?page=1&size=10", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "page" in data  # Cambiado de 'skip' a 'page'
        assert "pages" in data
        assert "size" in data
        assert "total" in data
        assert len(data["items"]) == 3

    def test_get_tareas_with_filters(self, client, auth_headers, clean_db, test_tarea_data):
        """Test filtros avanzados de tareas"""
        # Crear tareas con diferentes prioridades
        for i in range(3):
            tarea = test_tarea_data.copy()
            tarea["titulo"] = f"Tarea {i+1}"
            tarea["prioridad"] = i + 1
            tarea["completado"] = i % 2 == 0
            client.post("/tareas/", json=tarea, headers=auth_headers)
        
        # Filtrar por prioridad alta
        response = client.get("/tareas/?prioridad=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["prioridad"] == 3

    def test_rate_limit_tareas(self, client, auth_headers, clean_db, test_tarea_data):
        """Test rate limiting en operaciones de tareas"""
        # Crear múltiples tareas rápidamente
        for i in range(10):
            tarea = test_tarea_data.copy()
            tarea["titulo"] = f"Tarea {i+1}"
            response = client.post("/tareas/", json=tarea, headers=auth_headers)
            # Los primeros deberían funcionar, los últimos podrían ser rate limited
            assert response.status_code in [201, 429]


@pytest.mark.api
@pytest.mark.unit
class TestHealthCheck:
    """Pruebas para endpoints de health check"""

    def test_health_check_response(self, client):
        """Test del endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data


@pytest.mark.api
@pytest.mark.unit
class TestErrorHandling:
    """Pruebas para manejo de errores"""

    def test_invalid_json(self, client, clean_db):
        """Test manejo de JSON inválido"""
        response = client.post("/register", data="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_missing_required_fields(self, client, auth_headers, clean_db):
        """Test campos requeridos faltantes"""
        response = client.post("/tareas/", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_invalid_tarea_id_format(self, client, auth_headers, clean_db):
        """Test formato de ID de tarea inválido"""
        response = client.get("/tareas/invalid_id", headers=auth_headers)
        assert response.status_code == 422

    def test_invalid_sort_field(self, client, auth_headers, clean_db):
        """Test campo de ordenamiento inválido"""
        response = client.get("/tareas/?sort_by=invalid_field", headers=auth_headers)
        # Debería funcionar pero ignorar el campo inválido
        assert response.status_code == 200 