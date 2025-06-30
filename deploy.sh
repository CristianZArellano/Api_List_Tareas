#!/bin/bash

# Script de despliegue para la aplicación de tareas
# Uso: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Desplegando aplicación en modo: $ENVIRONMENT"

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [dev|prod]"
    echo ""
    echo "Opciones:"
    echo "  dev   - Despliegue de desarrollo (con volúmenes)"
    echo "  prod  - Despliegue de producción (sin volúmenes)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 dev   # Despliegue de desarrollo"
    echo "  $0 prod  # Despliegue de producción"
}

# Verificar argumentos
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "❌ Error: Modo inválido. Use 'dev' o 'prod'"
    show_help
    exit 1
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Limpiar imágenes si es producción
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo "🧹 Limpiando imágenes anteriores..."
    docker-compose down --rmi all --volumes --remove-orphans
fi

# Construir y levantar servicios
echo "🔨 Construyendo y levantando servicios..."
if [[ "$ENVIRONMENT" == "dev" ]]; then
    docker-compose up --build -d
else
    # Para producción, usar docker-compose.prod.yml si existe
    if [[ -f "docker-compose.prod.yml" ]]; then
        docker-compose -f docker-compose.prod.yml up --build -d
    else
        docker-compose up --build -d
    fi
fi

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

# Mostrar logs si hay errores
echo "📋 Últimos logs:"
docker-compose logs --tail=20

echo ""
echo "✅ Despliegue completado!"
echo ""
echo "🌐 URLs de acceso:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Comandos útiles:"
echo "  docker-compose logs -f    # Ver logs en tiempo real"
echo "  docker-compose down       # Detener servicios"
echo "  docker-compose restart    # Reiniciar servicios" 