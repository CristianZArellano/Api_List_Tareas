# API de Tareas

API REST para la gestión de tareas (To-Do) construida con FastAPI y SQLAlchemy.

## Características
- Crear, listar, actualizar y eliminar tareas.
- Filtros y paginación en la consulta de tareas.
- Documentación automática con Swagger UI y Redoc.
- Health check para monitoreo del servicio.

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

## Instalación y ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repo>
   cd list-Tareas
   ```
2. **Instalar dependencias:**
   ```bash
   pip install fastapi uvicorn sqlalchemy
   ```
3. **Ejecutar la API:**
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Acceder a la documentación interactiva:**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Notas
- La base de datos es SQLite y se crea automáticamente como `tareas.db` en la raíz del proyecto.
- Para producción, ajustar los orígenes permitidos en CORS y considerar una base de datos más robusta.

## Licencia
MIT 