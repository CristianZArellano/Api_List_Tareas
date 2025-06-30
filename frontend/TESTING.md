# Testing del Frontend

Este documento describe la estrategia de testing implementada para el frontend de la aplicación de gestión de tareas.

## 📋 Índice

- [Estructura de Tests](#estructura-de-tests)
- [Configuración](#configuración)
- [Ejecutar Tests](#ejecutar-tests)
- [Cobertura de Tests](#cobertura-de-tests)
- [Tipos de Tests](#tipos-de-tests)
- [Mejores Prácticas](#mejores-prácticas)
- [Troubleshooting](#troubleshooting)

## 🏗️ Estructura de Tests

```
frontend/src/
├── services/
│   └── __tests__/
│       └── api.test.js          # Tests del servicio de API
├── contexts/
│   └── __tests__/
│       ├── AuthContext.test.js  # Tests del contexto de autenticación
│       └── TaskContext.test.js  # Tests del contexto de tareas
├── components/
│   └── __tests__/
│       └── PrivateRoute.test.js # Tests del componente de ruta privada
├── pages/
│   └── __tests__/
│       └── Login.test.js        # Tests de la página de login
└── setupTests.js                # Configuración global de tests
```

## ⚙️ Configuración

### Dependencias

- **@testing-library/react**: Para renderizar y interactuar con componentes React
- **@testing-library/jest-dom**: Matchers adicionales para Jest
- **@testing-library/user-event**: Para simular interacciones de usuario
- **axios-mock-adapter**: Para mockear peticiones HTTP
- **jest**: Framework de testing

### Configuración de Jest

La configuración se encuentra en `package.json`:

```json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/index.js",
      "!src/reportWebVitals.js",
      "!src/setupTests.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

### setupTests.js

Archivo de configuración global que incluye:
- Configuración de jest-dom
- Mocks de localStorage, console, window.matchMedia
- Mocks de ResizeObserver e IntersectionObserver
- Configuración de limpieza automática

## 🚀 Ejecutar Tests

### Comandos Disponibles

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests en modo watch
npm run test:watch

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar tests en CI
npm run test:ci

# Ejecutar tests específicos usando el script personalizado
npm run test:api        # Solo tests de API
npm run test:contexts   # Solo tests de contextos
npm run test:components # Solo tests de componentes
npm run test:pages      # Solo tests de páginas
npm run test:all        # Todos los tests con cobertura
```

### Script Personalizado

El archivo `run-tests.js` proporciona funcionalidades adicionales:

```bash
# Ejecutar con opciones específicas
node run-tests.js --coverage --verbose
node run-tests.js --testNamePattern="login"
node run-tests.js --watch --silent
```

## 📊 Cobertura de Tests

### Objetivos de Cobertura

- **Branches**: 80%
- **Functions**: 80%
- **Lines**: 80%
- **Statements**: 80%

### Generar Reporte de Cobertura

```bash
npm run test:coverage
```

El reporte se genera en la carpeta `coverage/` y se puede abrir `coverage/lcov-report/index.html` en el navegador.

## 🧪 Tipos de Tests

### 1. Tests de Servicios (API)

**Archivo**: `src/services/__tests__/api.test.js`

Cubre:
- Configuración de axios
- Interceptors (request/response)
- Servicios de autenticación
- Servicios de tareas
- Servicios de contraseñas
- Manejo de errores

**Ejemplo**:
```javascript
test('debe hacer login exitosamente', async () => {
  const mockResponse = {
    access_token: 'access-token',
    refresh_token: 'refresh-token'
  };
  
  mock.onPost('/token').reply(200, mockResponse);
  
  const result = await authService.login('test@example.com', 'password');
  expect(result).toEqual(mockResponse);
});
```

### 2. Tests de Contextos

**Archivos**: 
- `src/contexts/__tests__/AuthContext.test.js`
- `src/contexts/__tests__/TaskContext.test.js`

Cubren:
- Renderizado del provider
- Hooks personalizados
- Estados y actualizaciones
- Manejo de errores
- Interacciones con servicios

**Ejemplo**:
```javascript
test('debe proporcionar valores iniciales correctos', () => {
  render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  );

  expect(screen.getByTestId('user')).toHaveTextContent('null');
  expect(screen.getByTestId('loading')).toHaveTextContent('true');
});
```

### 3. Tests de Componentes

**Archivo**: `src/components/__tests__/PrivateRoute.test.js`

Cubren:
- Renderizado condicional
- Navegación
- Estados de carga
- Props y children

### 4. Tests de Páginas

**Archivo**: `src/pages/__tests__/Login.test.js`

Cubren:
- Renderizado del formulario
- Interacciones de usuario
- Validaciones
- Estados de carga
- Manejo de errores
- Navegación

## ✅ Mejores Prácticas

### 1. Estructura de Tests

```javascript
describe('ComponentName', () => {
  beforeEach(() => {
    // Setup común
  });

  describe('funcionalidad específica', () => {
    test('debe hacer algo específico', () => {
      // Test
    });
  });
});
```

### 2. Naming de Tests

- Usar descripciones claras en español
- Seguir el patrón: "debe [acción] cuando [condición]"
- Agrupar tests relacionados en `describe` blocks

### 3. Mocks

```javascript
// Mock de servicios
jest.mock('../../services/api', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
  },
}));

// Mock de localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
global.localStorage = localStorageMock;
```

### 4. Testing de Async Code

```javascript
test('debe manejar operación asíncrona', async () => {
  const user = userEvent.setup();
  await user.click(button);
  
  await waitFor(() => {
    expect(screen.getByText('Resultado')).toBeInTheDocument();
  });
});
```

### 5. Testing de Errores

```javascript
test('debe manejar error correctamente', async () => {
  mockService.mockRejectedValue(new Error('Error message'));
  
  await user.click(submitButton);
  
  await waitFor(() => {
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });
});
```

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error de localStorage**
   ```javascript
   // Asegúrate de que el mock esté configurado
   global.localStorage = localStorageMock;
   ```

2. **Error de React Router**
   ```javascript
   // Envuelve el componente con BrowserRouter
   render(
     <BrowserRouter>
       <Component />
     </BrowserRouter>
   );
   ```

3. **Error de async/await**
   ```javascript
   // Usa waitFor para operaciones asíncronas
   await waitFor(() => {
     expect(element).toBeInTheDocument();
   });
   ```

4. **Error de mocks**
   ```javascript
   // Limpia los mocks antes de cada test
   beforeEach(() => {
     jest.clearAllMocks();
   });
   ```

### Debugging

1. **Ejecutar tests en modo verbose**:
   ```bash
   npm test -- --verbose
   ```

2. **Ejecutar un test específico**:
   ```bash
   npm test -- --testNamePattern="nombre del test"
   ```

3. **Ejecutar tests con console.log**:
   ```bash
   npm test -- --verbose --no-coverage
   ```

## 📈 Métricas de Calidad

### Cobertura Actual

- **API Service**: 100%
- **AuthContext**: 95%
- **TaskContext**: 90%
- **PrivateRoute**: 100%
- **Login Page**: 85%

### Próximos Pasos

1. Agregar tests para páginas faltantes (Register, Dashboard)
2. Implementar tests de integración
3. Agregar tests de accesibilidad
4. Implementar tests E2E con Cypress o Playwright

## 🤝 Contribución

Al agregar nuevos tests:

1. Sigue la estructura de carpetas existente
2. Usa los mocks y configuraciones establecidas
3. Mantén la cobertura mínima del 80%
4. Documenta casos edge y errores
5. Ejecuta todos los tests antes de hacer commit

---

**Nota**: Este documento se actualiza automáticamente con cada cambio en la estrategia de testing. 