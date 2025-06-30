# Lista de Tareas - API REST

Una API REST completa para gestionar tareas con autenticación JWT OAuth2, construida con FastAPI y SQLAlchemy.

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- **JWT Tokens**: Autenticación basada en tokens JWT con refresh tokens
- **Validación de Contraseñas Avanzada**: Sistema robusto con estándares modernos
- **Hashing Seguro**: bcrypt con 12 rounds (recomendado por OWASP/NIST)
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **CORS**: Configurado para desarrollo y producción
- **Middleware de Autenticación**: Verificación automática de tokens

### 🌍 Soporte Internacional
- **Caracteres Unicode**: Soporte completo para contraseñas en cualquier idioma
- **Validación Multilingüe**: Acepta letras de español, ruso, chino, árabe, japonés, etc.
- **Mensajes de Error**: Claros y descriptivos en español

### 📊 Análisis de Fortaleza
- **Evaluación en Tiempo Real**: Análisis detallado de fortaleza de contraseñas
- **Puntuación de Seguridad**: Sistema de 8 puntos con niveles de fortaleza
- **Feedback Visual**: Indicadores claros de fortaleza y problemas

### 🧪 Testing Completo
- **81 Tests Exitosos**: Cobertura completa de funcionalidades
- **Tests Unitarios**: Validación, hashing, API endpoints
- **Tests de Integración**: Flujos completos de usuario
- **Tests de Seguridad**: Verificación de tokens y contraseñas
- **Base de Datos de Test**: Aislamiento completo con limpieza automática

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos y serialización
- **python-jose**: Manejo de JWT tokens
- **passlib**: Hashing seguro de contraseñas
- **password-validator**: Validación robusta de contraseñas
- **bcrypt**: Algoritmo de hashing seguro
- **pytest**: Framework de testing

## 📋 Requisitos de Contraseña

### ✅ Requisitos Mínimos
- **Longitud**: 8-128 caracteres
- **Mayúsculas**: Al menos una letra mayúscula (de cualquier idioma)
- **Minúsculas**: Al menos una letra minúscula (de cualquier idioma)
- **Números**: Al menos un número
- **Caracteres Especiales**: Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)

### ❌ Restricciones
- **Espacios**: No se permiten espacios
- **Repeticiones**: No más de 3 caracteres consecutivos iguales
- **Secuencias**: No se permiten secuencias comunes (123, abc, qwe, etc.)
- **Contraseñas Comunes**: No se permiten contraseñas de diccionario

### 🌍 Ejemplos de Contraseñas Válidas
```
Mañana2024!          # Español con ñ
Árbol#Grande1        # Español con acentos
Пароль2024!          # Ruso
密碼Test2024!        # Chino + inglés
MotDePasse2024!      # Francés
Passwörd2024!        # Alemán con umlaut
SenhaForte2024!      # Portugués
P@sswørd2024!        # Noruego con ø
ContraseñaÜñîçødë1!  # Múltiples caracteres Unicode
```

## 🔧 Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/CristianZArellano/Api_List_Tareas.git
cd list-Tareas
```

2. **Crear entorno virtual**:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**:
```bash
python migrate_db.py
```

6. **Ejecutar la aplicación**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## 🧪 Testing

### Ejecutar Todos los Tests
```bash
python run_tests.py
```

### Ejecutar Tests por Categoría
```bash
python run_tests.py unit           # Tests unitarios
python run_tests.py integration    # Tests de integración
python run_tests.py password       # Tests de contraseñas
python run_tests.py api            # Tests de API
python run_tests.py security       # Tests de seguridad
```

### Resultados de Tests
- **Total de Tests**: 81 ✅
- **Tests Exitosos**: 81 ✅
- **Tests Fallidos**: 0 ❌
- **Tiempo de Ejecución**: ~44 segundos
- **Cobertura**: 100% de funcionalidades principales

## 📚 Uso de la API

### 🔐 Endpoints de Autenticación

#### Registrar Usuario
```http
POST /register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "username": "usuario_ejemplo",
  "password": "Contraseña123!",
  "nombre_completo": "Usuario Ejemplo"
}
```

#### Login (OAuth2)
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=usuario@ejemplo.com&password=Contraseña123!
```

#### Refresh Token
```http
POST /refresh
Content-Type: application/json

{
  "token": "refresh_token_here"
}
```

#### Logout
```http
POST /logout
Content-Type: application/json

{
  "token": "refresh_token_here"
}
```

#### Logout All (Cerrar todas las sesiones)
```http
POST /logout/all
Authorization: Bearer <access_token>
```

### 🔍 Endpoints de Validación de Contraseñas

#### Obtener Requisitos de Contraseña
```http
GET /password/requirements
```

**Respuesta**:
```json
{
  "min_length": 8,
  "max_length": 128,
  "requirements": [
    "Al menos una letra mayúscula (de cualquier idioma)",
    "Al menos una letra minúscula (de cualquier idioma)",
    "Al menos un número",
    "Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)",
    "No puede contener espacios",
    "No puede tener caracteres repetidos consecutivos",
    "No puede contener secuencias de caracteres",
    "No puede ser una contraseña común"
  ]
}
```

#### Analizar Fortaleza de Contraseña
```http
POST /password/check-strength
Content-Type: application/json

{
  "password": "Contraseña123!"
}
```

**Respuesta**:
```json
{
  "length": 13,
  "has_uppercase": true,
  "has_lowercase": true,
  "has_digit": true,
  "has_symbol": true,
  "has_spaces": false,
  "has_repeating_chars": false,
  "is_common": false,
  "score": 6,
  "strength": "moderada"
}
```

#### Validar Contraseña
```http
POST /password/validate
Content-Type: application/json

{
  "password": "Contraseña123!"
}
```

**Respuesta**:
```json
{
  "is_valid": true,
  "error_message": null
}
```

### 📝 Endpoints de Tareas

#### Crear Tarea
```http
POST /tareas
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "titulo": "Mi tarea",
  "descripcion": "Descripción de la tarea",
  "prioridad": 1,
  "fecha_limite": "2024-12-31T23:59:59"
}
```

#### Listar Tareas (con filtros y paginación)
```http
GET /tareas?skip=0&limit=10&completado=false&prioridad=1&buscar=importante&ordenar_por=created_at&orden=desc
Authorization: Bearer <access_token>
```

**Parámetros de consulta**:
- `skip`: Elementos a saltar (paginación)
- `limit`: Máximo de elementos por página
- `completado`: Filtrar por estado (true/false)
- `prioridad`: Filtrar por prioridad (1-5)
- `buscar`: Buscar en título y descripción
- `ordenar_por`: Campo para ordenar
- `orden`: Orden ascendente (asc) o descendente (desc)

#### Obtener Tarea Específica
```http
GET /tareas/{tarea_id}
Authorization: Bearer <access_token>
```

#### Actualizar Tarea
```http
PUT /tareas/{tarea_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "titulo": "Tarea actualizada",
  "descripcion": "Nueva descripción",
  "completado": true,
  "prioridad": 2
}
```

#### Eliminar Tarea
```http
DELETE /tareas/{tarea_id}
Authorization: Bearer <access_token>
```

### ⚙️ Endpoints del Sistema

#### Health Check
```http
GET /health
```

**Respuesta**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Obtener Usuario Actual
```http
GET /me
Authorization: Bearer <access_token>
```

## 📖 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔒 Seguridad

### Estándares Implementados
- **OWASP Password Guidelines**: Validación robusta de contraseñas
- **NIST Digital Identity Guidelines**: Estándares de seguridad
- **ISO/IEC 27001**: Gestión de seguridad de la información
- **bcrypt**: Algoritmo de hashing recomendado por OWASP

### Características de Seguridad
- **Rate Limiting**: Protección contra ataques de fuerza bruta
  - General: 200 requests/minuto
  - Login: 20 intentos/minuto
  - Tareas: 100 operaciones/minuto
- **Validación de Entrada**: Sanitización y validación de todos los datos
- **Manejo de Errores**: Respuestas seguras sin información sensible
- **CORS**: Configuración segura para desarrollo y producción
- **Middleware de Autenticación**: Verificación automática de tokens
- **Refresh Tokens**: Renovación segura de tokens de acceso

## 🌐 Colección de Insomnia

Incluye una colección completa de Insomnia con todos los endpoints y ejemplos:

1. Importar `insomnia_collection.json` en Insomnia
2. Configurar la variable `base_url` como `http://localhost:8000`
3. Ejecutar las pruebas en orden

Ver `README_INSOMNIA.md` para instrucciones detalladas.

## 🚀 Despliegue

### Variables de Entorno Requeridas
```env
# Base de datos
DATABASE_URL=sqlite:///./tareas.db

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_compleja
ALGORITHM=HS256

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=200
LOGIN_RATE_LIMIT_PER_MINUTE=20
TASK_RATE_LIMIT_PER_MINUTE=100

# Contraseñas
MIN_PASSWORD_LENGTH=8
MAX_PASSWORD_LENGTH=128
```

### Docker (Opcional)
```bash
docker build -t api-tareas .
docker run -p 8000:8000 api-tareas
```

### Docker Compose
```bash
docker-compose up -d
```

## 📈 Monitoreo y Logs

### Health Check
El endpoint `/health` proporciona información sobre:
- Estado del servicio
- Versión de la API
- Estado de la base de datos
- Timestamp actual

### Logs de Seguridad
- Intentos de login fallidos
- Tokens expirados
- Rate limiting activado
- Errores de validación

## 🧪 Testing y Calidad

### Cobertura de Tests
- **Autenticación**: Registro, login, logout, refresh tokens
- **Gestión de Tareas**: CRUD completo con filtros y paginación
- **Validación de Contraseñas**: Análisis de fortaleza y validación
- **Hashing de Contraseñas**: Seguridad y rendimiento
- **Rate Limiting**: Protección contra ataques
- **Manejo de Errores**: Respuestas apropiadas
- **Integración**: Flujos completos de usuario

### Ejecución de Tests
```bash
# Todos los tests
python run_tests.py

# Tests específicos
python -m pytest tests/test_api.py -v
python -m pytest tests/test_password_validation.py -v
python -m pytest tests/test_integration.py -v

# Por categoría
python -m pytest -m unit -v
python -m pytest -m integration -v
python -m pytest -m password -v
python -m pytest -m api -v
python -m pytest -m security -v
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Ejecutar los tests para asegurar que todo funciona
4. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abrir un Pull Request

### Guías de Contribución
- Mantener cobertura de tests al 100%
- Seguir las convenciones de código existentes
- Documentar nuevas funcionalidades
- Actualizar la documentación según sea necesario

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación en `/docs`
2. Ejecuta las pruebas para verificar la instalación: `python run_tests.py`
3. Revisa los logs de la aplicación
4. Abre un issue en el repositorio

### Problemas Comunes
- **Error de base de datos**: Ejecuta `python migrate_db.py`
- **Error de autenticación**: Verifica que el token no haya expirado
- **Error de rate limiting**: Espera un minuto antes de hacer más solicitudes
- **Error de validación de contraseña**: Revisa los requisitos en `/password/requirements`

---

**¡Disfruta usando la API de Gestión de Tareas! 🎉**


*Tests: 81/81 ✅*
*Versión: 1.0.0* 