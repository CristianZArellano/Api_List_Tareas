# 🚀 Guía de Despliegue - Aplicación de Tareas

Esta guía te ayudará a desplegar la aplicación de gestión de tareas en diferentes entornos.

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Git
- Al menos 2GB de RAM disponible
- Puertos 3000, 8000 y 5432 libres

## 🛠️ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd list-Tareas
```

### 2. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus valores
```

### 3. Desplegar con script automático
```bash
# Desarrollo
./deploy.sh dev

# Producción
./deploy.sh prod
```

## 🐳 Despliegue con Docker

### Opción 1: Despliegue de Desarrollo
```bash
# Construir y levantar todos los servicios
docker-compose up --build -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Opción 2: Despliegue de Producción
```bash
# Usar configuración de producción
docker-compose -f docker-compose.prod.yml up --build -d

# Con variables de entorno personalizadas
export POSTGRES_PASSWORD=tu_password_seguro
export SECRET_KEY=tu_secret_key_muy_largo
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🌐 URLs de Acceso

| Entorno | Frontend | Backend | API Docs | Base de Datos |
|---------|----------|---------|----------|---------------|
| Desarrollo | http://localhost:3000 | http://localhost:8000 | http://localhost:8000/docs | localhost:5432 |
| Producción | http://localhost | http://localhost:8000 | http://localhost:8000/docs | localhost:5432 |

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `env.example`:

```bash
# Base de datos
POSTGRES_PASSWORD=tu_password_seguro_aqui
DATABASE_URL=postgresql://postgres:tu_password_seguro_aqui@db:5432/tareas_db

# Seguridad
SECRET_KEY=tu_secret_key_muy_largo_y_seguro_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno
ENVIRONMENT=production

# URLs
REACT_APP_API_URL=http://localhost:8000
```

### Puertos

| Servicio | Puerto Desarrollo | Puerto Producción |
|----------|-------------------|-------------------|
| Frontend | 3000 | 80 |
| Backend | 8000 | 8000 |
| Base de Datos | 5432 | 5432 |
| HTTPS | - | 443 |

## 📊 Comandos de Gestión

### Verificar Estado
```bash
# Estado de todos los servicios
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db
```

### Mantenimiento
```bash
# Detener todos los servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart frontend

# Reconstruir un servicio
docker-compose build --no-cache frontend

# Limpiar recursos no utilizados
docker system prune -f
```

### Acceso a Contenedores
```bash
# Acceder al backend
docker-compose exec backend bash

# Acceder al frontend
docker-compose exec frontend sh

# Acceder a la base de datos
docker-compose exec db psql -U postgres -d tareas_db
```

## 🧪 Testing

### Frontend
```bash
cd frontend
npm test                    # Ejecutar tests
npm run test:coverage       # Tests con cobertura
npm run test:watch          # Tests en modo watch
```

### Backend
```bash
cd backend
python -m pytest           # Ejecutar tests
python -m pytest -v        # Tests con output detallado
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. Puerto ocupado
```bash
# Ver qué usa el puerto
sudo lsof -i :3000

# Detener servicios
docker-compose down

# Cambiar puerto en docker-compose.yml si es necesario
```

#### 2. Error de permisos de Docker
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar con sudo
sudo docker-compose up -d
```

#### 3. Base de datos no conecta
```bash
# Ver logs de la base de datos
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db

# Verificar variables de entorno
docker-compose exec backend env | grep DATABASE
```

#### 4. Frontend no carga
```bash
# Ver logs del frontend
docker-compose logs frontend

# Verificar configuración de Nginx
docker-compose exec frontend nginx -t

# Reconstruir frontend
docker-compose build --no-cache frontend
```

#### 5. Error de memoria
```bash
# Aumentar memoria disponible para Docker
# En Docker Desktop: Settings > Resources > Memory

# O reducir recursos en docker-compose.yml
```

### Logs Detallados

#### Ver todos los logs
```bash
docker-compose logs
```

#### Ver logs de un servicio específico
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

#### Seguir logs en tiempo real
```bash
docker-compose logs -f
```

## 🔒 Seguridad

### Configuración de Producción

1. **Cambiar contraseñas por defecto**
2. **Usar HTTPS en producción**
3. **Configurar firewall**
4. **Hacer backup regular de la base de datos**

### Variables Sensibles

Nunca commits variables sensibles:
```bash
# Agregar .env al .gitignore
echo ".env" >> .gitignore
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U postgres tareas_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres tareas_db < backup.sql
```

## 📈 Monitoreo

### Health Checks

Los servicios incluyen health checks automáticos:

- **Frontend**: http://localhost:3000/healthcheck.html
- **Backend**: http://localhost:8000/health
- **Base de datos**: Verificación automática

### Métricas

```bash
# Uso de recursos
docker stats

# Información de contenedores
docker-compose ps
```

## 🚀 Despliegue en la Nube

### AWS
```bash
# Usar AWS ECS o EC2
# Configurar security groups
# Usar RDS para base de datos
```

### Google Cloud
```bash
# Usar Google Cloud Run
# Configurar Cloud SQL
# Usar Cloud Build
```

### Azure
```bash
# Usar Azure Container Instances
# Configurar Azure Database
# Usar Azure DevOps
```

## 📞 Soporte

Si encuentras problemas:

1. Revisar esta guía de solución de problemas
2. Verificar logs: `docker-compose logs`
3. Crear issue en el repositorio con:
   - Descripción del problema
   - Logs relevantes
   - Pasos para reproducir
   - Configuración del entorno

## 📝 Changelog

### v1.0.0
- Despliegue inicial con Docker
- Frontend React con Nginx
- Backend FastAPI
- Base de datos PostgreSQL
- Tests completos
- Scripts de despliegue automatizados 