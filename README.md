# 📋 Aplicación de Gestión de Tareas

Una aplicación completa de gestión de tareas con frontend en React y backend en FastAPI.

## 🚀 Características

- **Frontend**: React con hooks, context API y routing
- **Backend**: FastAPI con autenticación JWT
- **Base de datos**: PostgreSQL
- **Tests**: Cobertura completa de tests para frontend y backend
- **Docker**: Configuración completa para desarrollo y producción

## 📁 Estructura del Proyecto

```
list-Tareas/
├── frontend/          # Aplicación React
├── backend/           # API FastAPI
├── docker-compose.yml # Orquestación de servicios
├── deploy.sh         # Script de despliegue
└── README.md         # Este archivo
```

## 🛠️ Instalación y Despliegue

### Opción 1: Despliegue Rápido con Docker

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/CristianZArellano/Api_List_Tareas.git
   cd list-Tareas
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp env.example .env
   # Editar .env con tus valores
   ```

3. **Desplegar con el script:**
   ```bash
   # Desarrollo
   ./deploy.sh dev
   
   # Producción
   ./deploy.sh prod
   ```

### Opción 2: Despliegue Manual

1. **Levantar servicios:**
   ```bash
   # Desarrollo
   docker-compose up --build -d
   
   # Producción
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Verificar servicios:**
   ```bash
   docker-compose ps
   ```

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:3000 (desarrollo) / http://localhost (producción)
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 🧪 Ejecutar Tests

### Frontend
```bash
cd frontend
npm test                    # Ejecutar todos los tests
npm run test:coverage       # Tests con cobertura
npm run test:watch          # Tests en modo watch
```

### Backend
```bash
cd backend
python -m pytest           # Ejecutar todos los tests
python -m pytest -v        # Tests con output detallado
```

## 📊 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver estado de servicios
docker-compose ps

# Acceder a contenedor específico
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🔧 Configuración

### Variables de Entorno

Copia `env.example` a `.env` y configura:

- `POSTGRES_PASSWORD`: Contraseña de la base de datos
- `SECRET_KEY`: Clave secreta para JWT
- `REACT_APP_API_URL`: URL del backend

### Puertos

- **3000**: Frontend (desarrollo)
- **8000**: Backend API
- **5432**: PostgreSQL
- **80**: Frontend (producción)
- **443**: HTTPS (producción)

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Puerto ocupado:**
   ```bash
   sudo lsof -i :3000  # Ver qué usa el puerto
   docker-compose down  # Detener servicios
   ```

2. **Base de datos no conecta:**
   ```bash
   docker-compose logs db    # Ver logs de DB
   docker-compose restart db # Reiniciar DB
   ```

3. **Frontend no carga:**
   ```bash
   docker-compose logs frontend
   docker-compose restart frontend
   ```

### Logs Detallados

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

## 📈 Monitoreo

### Health Checks

Los servicios incluyen health checks automáticos:

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost/healthcheck.html
- **Database**: Verificación automática de conexión

### Métricas

```bash
# Ver uso de recursos
docker stats

# Ver información de contenedores
docker-compose ps
```

## 🔒 Seguridad

- JWT tokens con expiración configurable
- Validación de contraseñas robusta
- Headers de seguridad en Nginx
- Variables de entorno para configuración sensible

## 📝 Desarrollo

### Estructura de Tests

```
frontend/src/
├── components/__tests__/
├── contexts/__tests__/
├── pages/__tests__/
└── services/__tests__/

backend/tests/
├── test_api.py
├── test_integration.py
└── test_password_validation.py
```

### Agregar Nuevos Tests

1. Crear archivo `__tests__/` en el directorio correspondiente
2. Seguir convención de nombres: `ComponentName.test.js`
3. Ejecutar: `npm test` o `python -m pytest`

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas:

1. Revisar la sección de solución de problemas
2. Verificar logs: `docker-compose logs`
3. Crear issue en el repositorio con detalles del problema 