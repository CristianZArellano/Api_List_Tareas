# 📋 Guía de Uso - Colección Insomnia

## 🚀 Configuración Inicial

### 1. Importar la Colección
1. Abre Insomnia
2. Ve a **Settings** → **Data** → **Import Data**
3. Selecciona **From File** y elige `insomnia_collection.json`
4. La colección se importará automáticamente

### 2. Configurar el Entorno
1. En el panel izquierdo, busca **"API Gestión de Tareas"**
2. Haz clic en el selector de entorno (arriba a la derecha)
3. Selecciona **"Desarrollo"** para usar `http://127.0.0.1:8000`

### 3. Verificar que tu API esté ejecutándose
```bash
# En tu terminal, desde el directorio del proyecto
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 🔧 Solución de Problemas

### Error: "Couldn't resolve host name"
Si ves este error con `{{ _.base_url }}`:

**Solución 1: Usar URL directa**
- Usa el request **"Health Check (URL Directa)"** que tiene la URL completa
- URL: `http://127.0.0.1:8000/health`

**Solución 2: Verificar entorno**
1. Asegúrate de que el entorno "Desarrollo" esté seleccionado
2. Verifica que la variable `base_url` tenga el valor `http://127.0.0.1:8000`

**Solución 3: Configurar entorno manualmente**
1. Ve a **Settings** → **Environments**
2. Selecciona el entorno "Desarrollo"
3. Verifica que `base_url` = `http://127.0.0.1:8000`

## 📖 Flujo de Uso Recomendado

### 1. Probar Conexión
- Ejecuta **"Health Check (URL Directa)"** para verificar que la API esté funcionando
- Deberías recibir una respuesta como:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T...",
  "database": "connected"
}
```

### 2. Registrar Usuario
- Ejecuta **"Registrar Usuario"**
- Modifica el JSON según necesites:
```json
{
  "email": "tu-email@ejemplo.com",
  "username": "tu_usuario",
  "password": "Contraseña123!",
  "nombre_completo": "Tu Nombre"
}
```

### 3. Hacer Login
- Ejecuta **"Login (OAuth2)"**
- Usa las mismas credenciales del registro
- **Guarda** el `access_token` y `refresh_token` de la respuesta

### 4. Configurar Tokens
1. Ve a **Settings** → **Environments**
2. Selecciona "Desarrollo"
3. Actualiza las variables:
   - `access_token`: [token del paso anterior]
   - `refresh_token`: [refresh token del paso anterior]

### 5. Usar Endpoints de Tareas
Ahora puedes usar todos los endpoints de tareas:
- **Crear Tarea**
- **Listar Tareas**
- **Obtener Tarea**
- **Actualizar Tarea**
- **Eliminar Tarea**

## 🔐 Variables de Entorno

### Desarrollo
- `base_url`: `http://127.0.0.1:8000`
- `access_token`: [se llena después del login]
- `refresh_token`: [se llena después del login]
- `tarea_id`: `1` (se actualiza al crear tareas)

### Producción
- `base_url`: `https://tu-api-produccion.com`
- `access_token`: [se llena después del login]
- `refresh_token`: [se llena después del login]
- `tarea_id`: `1`

## 📝 Ejemplos de Uso

### Crear una Tarea
```json
{
  "titulo": "Completar documentación",
  "descripcion": "Finalizar la documentación de la API",
  "prioridad": 2,
  "completado": false
}
```

### Listar Tareas con Filtros
```
GET /tareas?skip=0&limit=10&completado=false&prioridad=2&buscar=documentación&ordenar_por=created_at&orden=desc
```

### Actualizar Tarea
```json
{
  "titulo": "Documentación completada",
  "completado": true,
  "prioridad": 1
}
```

## ⚠️ Rate Limits

- **Login**: 5 intentos por minuto por IP
- **Tareas**: 30 requests por minuto por IP
- **Otros endpoints**: 60 requests por minuto por IP

## 🆘 Troubleshooting

### La API no responde
1. Verifica que esté ejecutándose: `http://127.0.0.1:8000/health`
2. Revisa los logs del servidor
3. Verifica que el puerto 8000 esté libre

### Error de autenticación
1. Verifica que el token no haya expirado
2. Haz un nuevo login para obtener tokens frescos
3. Usa el endpoint de refresh si tienes un refresh token válido

### Error de validación
1. Revisa los requisitos de contraseña
2. Verifica el formato del JSON
3. Usa los endpoints de validación de contraseña para debuggear

## 📚 Endpoints Disponibles

### 🔐 Autenticación
- `POST /register` - Registrar usuario
- `POST /token` - Login OAuth2
- `POST /refresh` - Refrescar token
- `POST /logout` - Cerrar sesión
- `POST /logout/all` - Cerrar todas las sesiones
- `GET /me` - Obtener usuario actual
- `GET /password/requirements` - Requisitos de contraseña
- `POST /password/check-strength` - Analizar fortaleza
- `POST /password/validate` - Validar contraseña

### 📋 Tareas
- `POST /tareas` - Crear tarea
- `GET /tareas` - Listar tareas
- `GET /tareas/{id}` - Obtener tarea
- `PUT /tareas/{id}` - Actualizar tarea
- `DELETE /tareas/{id}` - Eliminar tarea

### ⚙️ Sistema
- `GET /health` - Health check
- `GET /` - Root endpoint 