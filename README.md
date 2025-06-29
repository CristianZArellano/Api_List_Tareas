# Lista de Tareas - API REST

Una API REST completa para gestionar tareas con autenticación JWT, construida con FastAPI y SQLAlchemy.

## Características

- 🔐 **Autenticación JWT**: Registro, login y gestión de usuarios
- 📝 **CRUD de Tareas**: Crear, leer, actualizar y eliminar tareas
- 👤 **Multi-usuario**: Cada usuario ve solo sus propias tareas
- 🔍 **Filtros y Paginación**: Filtrar por estado y paginar resultados
- 🛡️ **Validación de Datos**: Validación automática con Pydantic
- 🏥 **Health Check**: Endpoint para verificar el estado del servicio
- 🚀 **Documentación Automática**: Swagger UI en `/docs`

## Modelos de datos

### Tarea
| Campo        | Tipo     | Descripción                        |
|--------------|----------|------------------------------------|
| id           | int      | Identificador único (autogenerado) |
| titulo       | str      | Título de la tarea                 |
| descripcion  | str/null | Descripción opcional               |
| completado   | bool     | Estado de la tarea (completada)    |

## Endpoints principales

| Método | Ruta                | Descripción                                              |
|--------|---------------------|---------------------------------------------------------|
| POST   | `/tareas`           | Crear nueva tarea                                        |
| GET    | `/tareas`           | Listar todas las tareas (paginación y filtro opcional)   |
| GET    | `/tareas/{tarea_id}`| Obtener tarea por ID                                     |
| PUT    | `/tareas/{tarea_id}`| Actualizar tarea existente                               |
| DELETE | `/tareas/{tarea_id}`| Eliminar tarea por ID                                    |
| GET    | `/health`           | Verificar estado del servicio y la base de datos         |

## Ejemplos de uso

### Crear tarea
```json
POST /tareas
{
  "titulo": "Comprar pan",
  "descripcion": "Ir a la panadería antes de las 10am",
  "completado": false
}
```

### Listar tareas
```http
GET /tareas?skip=0&limit=10&completado=false
```

### Obtener tarea por ID
```http
GET /tareas/1
```

### Actualizar tarea
```json
PUT /tareas/1
{
  "titulo": "Comprar pan y leche",
  "completado": true
}
```

### Eliminar tarea
```http
DELETE /tareas/1
```

### Health check
```http
GET /health
```
Respuesta:
```json
{
  "status": "ok",
  "database": "connected"
}
```

## Esquemas de datos

### Crear tarea (`TareaCrear`)
| Campo        | Tipo     | Requerido | Descripción              |
|--------------|----------|-----------|--------------------------|
| titulo       | str      | Sí        | Título de la tarea       |
| descripcion  | str/null | No        | Descripción opcional     |
| completado   | bool     | No        | Por defecto: false       |

### Actualizar tarea (`TareaActualizar`)
Todos los campos son opcionales.

### Respuesta de tarea (`Tarea`)
Incluye todos los campos más el `id`.

## Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd list-Tareas
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Autenticación
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Iniciar sesión
- `GET /me` - Obtener información del usuario actual

### Tareas
- `POST /tareas` - Crear nueva tarea
- `GET /tareas` - Listar tareas (con filtros y paginación)
- `GET /tareas/{id}` - Obtener tarea específica
- `PUT /tareas/{id}` - Actualizar tarea
- `DELETE /tareas/{id}` - Eliminar tarea

### Sistema
- `GET /health` - Verificar estado del servicio

## Testing

### Instalación de dependencias de testing

Las dependencias de testing ya están incluidas en `requirements.txt`:
- `pytest` - Framework de testing
- `httpx` - Cliente HTTP para testing

### Ejecutar tests

**Ejecutar todos los tests:**
```bash
python run_tests.py
```

**Ejecutar tests con pytest directamente:**
```bash
pytest test_api.py -v
```

**Ejecutar un test específico:**
```bash
python run_tests.py TestAuthentication::test_register_user_success
```

**Ejecutar tests con más detalle:**
```bash
pytest test_api.py -v --tb=long
```

### Cobertura de tests

Los tests cubren:

#### 🔐 Autenticación
- ✅ Registro exitoso de usuarios
- ✅ Validación de emails duplicados
- ✅ Validación de usernames duplicados
- ✅ Validación de datos inválidos
- ✅ Login exitoso
- ✅ Login con credenciales inválidas
- ✅ Acceso a endpoints protegidos con token
- ✅ Rechazo de tokens inválidos

#### 📝 Gestión de Tareas
- ✅ Creación de tareas
- ✅ Listado de tareas (vacío y con datos)
- ✅ Paginación de resultados
- ✅ Filtros por estado (completado/pendiente)
- ✅ Obtención de tarea por ID
- ✅ Actualización de tareas
- ✅ Eliminación de tareas
- ✅ Aislamiento entre usuarios (un usuario no puede ver/modificar tareas de otro)

#### 🛡️ Manejo de Errores
- ✅ Validación de JSON inválido
- ✅ Campos requeridos faltantes
- ✅ IDs de tarea en formato inválido
- ✅ Recursos no encontrados (404)
- ✅ Acceso no autorizado (401)

#### 🏥 Health Check
- ✅ Verificación del estado del servicio

### Estructura de tests

```
test_api.py
├── TestAuthentication     # Tests de autenticación
├── TestTareas            # Tests de gestión de tareas
├── TestHealthCheck       # Tests de health check
└── TestErrorHandling     # Tests de manejo de errores
```

### Configuración de testing

- **Base de datos**: SQLite en memoria para tests
- **Fixtures**: Configuración automática de cliente y base de datos
- **Aislamiento**: Cada test tiene su propia base de datos limpia
- **Autenticación**: Fixtures para generar tokens de prueba

## Uso de la API

### 1. Registrar un usuario
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "usuario@example.com",
       "username": "usuario1",
       "password": "password123"
     }'
```

### 2. Iniciar sesión
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "usuario@example.com",
       "password": "password123"
     }'
```

### 3. Crear una tarea
```bash
curl -X POST "http://localhost:8000/tareas" \
     -H "Authorization: Bearer <tu-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "titulo": "Mi primera tarea",
       "descripcion": "Descripción de la tarea",
       "completado": false
     }'
```

### 4. Listar tareas
```bash
curl -X GET "http://localhost:8000/tareas" \
     -H "Authorization: Bearer <tu-token>"
```

## Estructura del Proyecto

```
list-Tareas/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicación principal y endpoints
│   ├── models.py        # Modelos de SQLAlchemy
│   ├── schemas.py       # Esquemas de Pydantic
│   ├── crud.py          # Operaciones de base de datos
│   ├── database.py      # Configuración de base de datos
│   ├── security.py      # Autenticación y JWT
│   └── config.py        # Configuración de la aplicación
├── test_api.py          # Tests de la API
├── conftest.py          # Configuración de pytest
├── pytest.ini          # Configuración de pytest
├── run_tests.py         # Script para ejecutar tests
├── requirements.txt     # Dependencias del proyecto
├── tareas.db           # Base de datos SQLite
└── README.md           # Este archivo
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos
- **JWT**: Autenticación con tokens
- **SQLite**: Base de datos ligera
- **Pytest**: Framework de testing
- **Uvicorn**: Servidor ASGI

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 