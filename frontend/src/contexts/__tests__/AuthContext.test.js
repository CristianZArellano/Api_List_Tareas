import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '../AuthContext';
import { authService } from '../../services/api';

// Mock del servicio de API
jest.mock('../../services/api', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    logoutAll: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

// Mock de localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Componente de prueba para usar el contexto
const TestComponent = () => {
  const { user, loading, error, login, register, logout, logoutAll, clearError, isAuthenticated } = useAuth();
  
  return (
    <div>
      <div data-testid="user">{user ? JSON.stringify(user) : 'null'}</div>
      <div data-testid="loading">{loading.toString()}</div>
      <div data-testid="error">{error || 'null'}</div>
      <div data-testid="isAuthenticated">{isAuthenticated.toString()}</div>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={() => register('testuser', 'test@example.com', 'password')}>Register</button>
      <button onClick={logout}>Logout</button>
      <button onClick={logoutAll}>Logout All</button>
      <button onClick={clearError}>Clear Error</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  describe('AuthProvider', () => {
    test('debe renderizar children correctamente', () => {
      render(
        <AuthProvider>
          <div data-testid="child">Test Child</div>
        </AuthProvider>
      );
      
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    test('debe verificar autenticación al cargar con token válido', async () => {
      const mockUser = { id: 1, email: 'test@example.com', full_name: 'Test User' };
      localStorageMock.getItem.mockReturnValue('valid-token');
      authService.getCurrentUser.mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });

    test('debe manejar error de autenticación al cargar', async () => {
      localStorageMock.getItem.mockReturnValue('invalid-token');
      authService.getCurrentUser.mockRejectedValue({ response: { status: 401 } });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    test('debe manejar error no relacionado con autenticación al cargar', async () => {
      localStorageMock.getItem.mockReturnValue('valid-token');
      authService.getCurrentUser.mockRejectedValue({ response: { status: 500 } });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    });
  });

  describe('useAuth hook', () => {
    test('debe lanzar error si se usa fuera del provider', () => {
      // Suprimir console.error para este test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => render(<TestComponent />)).toThrow('useAuth debe ser usado dentro de un AuthProvider');
      
      consoleSpy.mockRestore();
    });

    test('debe proporcionar valores iniciales correctos', () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(screen.getByTestId('loading')).toHaveTextContent('true');
      expect(screen.getByTestId('error')).toHaveTextContent('null');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  describe('login', () => {
    test('debe hacer login exitosamente', async () => {
      const mockLoginResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer'
      };
      const mockUser = { id: 1, email: 'test@example.com', full_name: 'Test User' };
      
      authService.login.mockResolvedValue(mockLoginResponse);
      authService.getCurrentUser.mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith('test@example.com', 'password');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'access-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-token');
        expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
        expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
      });
    });

    test('debe manejar error de login', async () => {
      const errorMessage = 'Invalid credentials';
      authService.login.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });

    test('debe manejar error de login sin respuesta del servidor', async () => {
      authService.login.mockRejectedValue(new Error('Network error'));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Error al iniciar sesión');
      });
    });
  });

  describe('register', () => {
    test('debe registrar usuario exitosamente', async () => {
      authService.register.mockResolvedValue({ id: 1, email: 'test@example.com' });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Register'));

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password'
        });
      });
    });

    test('debe manejar error de registro', async () => {
      const errorMessage = 'Email already exists';
      authService.register.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Register'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });
  });

  describe('logout', () => {
    test('debe hacer logout exitosamente', async () => {
      authService.logout.mockResolvedValue();

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(authService.logout).toHaveBeenCalled();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      });
    });

    test('debe manejar error de logout', async () => {
      authService.logout.mockRejectedValue(new Error('Logout error'));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      });
    });
  });

  describe('logoutAll', () => {
    test('debe hacer logout de todas las sesiones', async () => {
      authService.logoutAll.mockResolvedValue();

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      await user.click(screen.getByText('Logout All'));

      await waitFor(() => {
        expect(authService.logoutAll).toHaveBeenCalled();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      });
    });
  });

  describe('clearError', () => {
    test('debe limpiar el error', async () => {
      const errorMessage = 'Test error';
      authService.login.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      const user = userEvent.setup();
      
      // Primero generar un error
      await user.click(screen.getByText('Login'));
      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });

      // Luego limpiar el error
      await user.click(screen.getByText('Clear Error'));
      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('null');
      });
    });
  });
}); 