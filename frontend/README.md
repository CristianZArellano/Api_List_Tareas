# Frontend - Gestión de Tareas

Frontend React para la aplicación de gestión de tareas.

## Características

- 🔐 Autenticación JWT con refresh tokens
- 📋 CRUD completo de tareas
- 🔍 Filtrado y búsqueda de tareas
- 📱 Diseño responsive
- 🎨 Interfaz moderna y intuitiva

## Instalación

```bash
# Instalar dependencias
npm install

# Iniciar en modo desarrollo
npm start
```

## Configuración

El frontend se conecta automáticamente al backend en `http://localhost:8000` durante el desarrollo.

Para producción, configura la variable de entorno `REACT_APP_API_URL`:

```bash
REACT_APP_API_URL=https://tu-api.com
```

## Scripts Disponibles

- `npm start` - Inicia el servidor de desarrollo
- `npm build` - Construye la aplicación para producción
- `npm test` - Ejecuta las pruebas
- `npm eject` - Expone la configuración de webpack

## Estructura del Proyecto

```
src/
├── components/     # Componentes reutilizables
├── pages/         # Páginas principales
├── services/      # Servicios de API
├── hooks/         # Custom hooks
├── utils/         # Utilidades
└── styles/        # Estilos CSS
```

## Tecnologías

- React 18
- React Router DOM
- Axios para HTTP
- CSS Modules
- Local Storage para persistencia 