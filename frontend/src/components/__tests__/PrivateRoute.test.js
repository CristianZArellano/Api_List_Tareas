import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PrivateRoute from '../PrivateRoute';
import { AuthContext } from '../../contexts/AuthContext';

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({ to, replace }) => {
    mockNavigate(to, replace);
    return <div data-testid="navigate">Navigate to {to}</div>;
  },
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

describe('PrivateRoute', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  test('debe mostrar indicador de carga cuando loading es true', () => {
    const authValue = {
      isAuthenticated: false,
      loading: true,
    };

    renderWithRouter(
      <PrivateRoute>
        <div data-testid="protected-content">Protected Content</div>
      </PrivateRoute>,
      authValue
    );

    expect(screen.getByText('Cargando...')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('debe redirigir a login cuando no está autenticado', () => {
    const authValue = {
      isAuthenticated: false,
      loading: false,
    };

    renderWithRouter(
      <PrivateRoute>
        <div data-testid="protected-content">Protected Content</div>
      </PrivateRoute>,
      authValue
    );

    expect(screen.getByTestId('navigate')).toHaveTextContent('Navigate to /login');
    expect(mockNavigate).toHaveBeenCalledWith('/login', true);
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('debe mostrar contenido protegido cuando está autenticado', () => {
    const authValue = {
      isAuthenticated: true,
      loading: false,
    };

    renderWithRouter(
      <PrivateRoute>
        <div data-testid="protected-content">Protected Content</div>
      </PrivateRoute>,
      authValue
    );

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.queryByText('Cargando...')).not.toBeInTheDocument();
    expect(screen.queryByTestId('navigate')).not.toBeInTheDocument();
  });

  test('debe renderizar children correctamente', () => {
    const authValue = {
      isAuthenticated: true,
      loading: false,
    };

    renderWithRouter(
      <PrivateRoute>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
      </PrivateRoute>,
      authValue
    );

    expect(screen.getByTestId('child-1')).toBeInTheDocument();
    expect(screen.getByTestId('child-2')).toBeInTheDocument();
  });
}); 