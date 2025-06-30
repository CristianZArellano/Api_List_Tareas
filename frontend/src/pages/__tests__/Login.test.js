import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { AuthContext } from '../../contexts/AuthContext';

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const renderWithRouter = (component, authValue) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        {component}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Login', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  describe('Renderizado inicial', () => {
    test('debe renderizar el formulario de login correctamente', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
      expect(screen.getByLabelText('Email:')).toBeInTheDocument();
      expect(screen.getByLabelText('Contraseña:')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Iniciar Sesión' })).toBeInTheDocument();
      expect(screen.getByText('¿No tienes cuenta?')).toBeInTheDocument();
      expect(screen.getByText('Regístrate aquí')).toBeInTheDocument();
    });

    test('debe mostrar indicador de carga cuando authLoading es true', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: true,
      };

      renderWithRouter(<Login />, authValue);

      expect(screen.getByText('Cargando...')).toBeInTheDocument();
      expect(screen.queryByText('Iniciar Sesión')).not.toBeInTheDocument();
    });

    test('debe redirigir a dashboard si ya está autenticado', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: true,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('Interacción del formulario', () => {
    test('debe actualizar campos del formulario al escribir', async () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');

      const user = userEvent.setup();
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');

      expect(emailInput).toHaveValue('test@example.com');
      expect(passwordInput).toHaveValue('password123');
    });

    test('debe validar campos requeridos', async () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });
      const user = userEvent.setup();
      
      await user.click(submitButton);

      // Los campos HTML5 required deberían prevenir el envío
      expect(authValue.login).not.toHaveBeenCalled();
    });
  });

  describe('Envío del formulario', () => {
    test('debe hacer login exitosamente', async () => {
      const mockLogin = jest.fn().mockResolvedValue({ success: true });
      const authValue = {
        login: mockLogin,
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');
      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });

      const user = userEvent.setup();
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });

      // Los campos deberían limpiarse después del login exitoso
      expect(emailInput).toHaveValue('');
      expect(passwordInput).toHaveValue('');
    });

    test('debe mostrar error cuando el login falla', async () => {
      const errorMessage = 'Credenciales inválidas';
      const mockLogin = jest.fn().mockRejectedValue(new Error(errorMessage));
      const authValue = {
        login: mockLogin,
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');
      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });

      const user = userEvent.setup();
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    test('debe mostrar estado de carga durante el login', async () => {
      const mockLogin = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      const authValue = {
        login: mockLogin,
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');
      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });

      const user = userEvent.setup();
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      // Debería mostrar estado de carga
      expect(screen.getByText('Iniciando sesión...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();

      await waitFor(() => {
        expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
      });
    });

    test('debe manejar error sin mensaje específico', async () => {
      const mockLogin = jest.fn().mockRejectedValue(new Error());
      const authValue = {
        login: mockLogin,
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');
      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });

      const user = userEvent.setup();
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Error al iniciar sesión')).toBeInTheDocument();
      });
    });
  });

  describe('Navegación', () => {
    test('debe tener enlace a la página de registro', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const registerLink = screen.getByText('Regístrate aquí');
      expect(registerLink).toBeInTheDocument();
      expect(registerLink.closest('a')).toHaveAttribute('href', '/register');
    });
  });

  describe('Accesibilidad', () => {
    test('debe tener labels asociados correctamente', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const emailInput = screen.getByLabelText('Email:');
      const passwordInput = screen.getByLabelText('Contraseña:');

      expect(emailInput).toHaveAttribute('type', 'email');
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('debe tener botón de envío accesible', () => {
      const authValue = {
        login: jest.fn(),
        isAuthenticated: false,
        loading: false,
      };

      renderWithRouter(<Login />, authValue);

      const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });
      expect(submitButton).toHaveAttribute('type', 'submit');
    });
  });
}); 