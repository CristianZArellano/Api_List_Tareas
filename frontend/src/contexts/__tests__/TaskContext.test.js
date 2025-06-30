import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskProvider, useTasks } from '../TaskContext';
import { taskService } from '../../services/api';

// Mock del servicio de API
jest.mock('../../services/api', () => ({
  taskService: {
    getTasks: jest.fn(),
    getTask: jest.fn(),
    createTask: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn(),
  },
}));

// Mock de console.log para evitar ruido en los tests
const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

// Componente de prueba para usar el contexto
const TestComponent = () => {
  const {
    tasks,
    loading,
    error,
    pagination,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskStatus,
    clearError,
  } = useTasks();
  
  return (
    <div>
      <div data-testid="tasks">{JSON.stringify(tasks)}</div>
      <div data-testid="loading">{loading.toString()}</div>
      <div data-testid="error">{error || 'null'}</div>
      <div data-testid="pagination">{JSON.stringify(pagination)}</div>
      <button onClick={() => fetchTasks()}>Fetch Tasks</button>
      <button onClick={() => fetchTasks({ completed: true })}>Fetch Completed</button>
      <button onClick={() => createTask({ title: 'New Task', description: 'Test' })}>Create Task</button>
      <button onClick={() => updateTask(1, { title: 'Updated Task' })}>Update Task</button>
      <button onClick={() => deleteTask(1)}>Delete Task</button>
      <button onClick={() => toggleTaskStatus(1, true)}>Toggle Status</button>
      <button onClick={clearError}>Clear Error</button>
    </div>
  );
};

describe('TaskContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    consoleSpy.mockClear();
    consoleErrorSpy.mockClear();
  });

  afterAll(() => {
    consoleSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  describe('TaskProvider', () => {
    test('debe renderizar children correctamente', () => {
      render(
        <TaskProvider>
          <div data-testid="child">Test Child</div>
        </TaskProvider>
      );
      
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    test('debe proporcionar valores iniciales correctos', () => {
      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      expect(screen.getByTestId('tasks')).toHaveTextContent('[]');
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
      expect(screen.getByTestId('error')).toHaveTextContent('null');
      expect(screen.getByTestId('pagination')).toHaveTextContent(JSON.stringify({
        total: 0,
        page: 1,
        size: 10,
        pages: 0
      }));
    });
  });

  describe('useTasks hook', () => {
    test('debe lanzar error si se usa fuera del provider', () => {
      expect(() => render(<TestComponent />)).toThrow('useTasks debe ser usado dentro de un TaskProvider');
    });
  });

  describe('fetchTasks', () => {
    test('debe obtener tareas exitosamente', async () => {
      const mockResponse = {
        items: [
          { id: 1, title: 'Tarea 1', completed: false },
          { id: 2, title: 'Tarea 2', completed: true }
        ],
        total: 2,
        page: 1,
        size: 10,
        pages: 1
      };
      
      taskService.getTasks.mockResolvedValue(mockResponse);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Fetch Tasks'));

      await waitFor(() => {
        expect(taskService.getTasks).toHaveBeenCalledWith({});
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(mockResponse.items));
        expect(screen.getByTestId('pagination')).toHaveTextContent(JSON.stringify({
          total: 2,
          page: 1,
          size: 10,
          pages: 1
        }));
      });
    });

    test('debe obtener tareas con parámetros', async () => {
      const mockResponse = {
        items: [{ id: 2, title: 'Tarea 2', completed: true }],
        total: 1,
        page: 1,
        size: 10,
        pages: 1
      };
      
      taskService.getTasks.mockResolvedValue(mockResponse);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Fetch Completed'));

      await waitFor(() => {
        expect(taskService.getTasks).toHaveBeenCalledWith({ completed: true });
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(mockResponse.items));
      });
    });

    test('debe manejar error al obtener tareas', async () => {
      const errorMessage = 'Error al cargar tareas';
      taskService.getTasks.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Fetch Tasks'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });

    test('debe manejar error 429 (Too Many Requests) con reintentos', async () => {
      const mockResponse = {
        items: [{ id: 1, title: 'Tarea 1', completed: false }],
        total: 1,
        page: 1,
        size: 10,
        pages: 1
      };

      // Primera llamada falla con 429, segunda es exitosa
      taskService.getTasks
        .mockRejectedValueOnce({
          response: {
            status: 429,
            headers: { 'retry-after': '1' },
            data: { detail: 'Too many requests' }
          }
        })
        .mockResolvedValueOnce(mockResponse);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Fetch Tasks'));

      await waitFor(() => {
        expect(taskService.getTasks).toHaveBeenCalledTimes(2);
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(mockResponse.items));
      }, { timeout: 5000 });
    });

    test('debe manejar error 429 después de 3 reintentos', async () => {
      const errorMessage = 'Too many requests';
      
      taskService.getTasks.mockRejectedValue({
        response: {
          status: 429,
          headers: { 'retry-after': '1' },
          data: { detail: errorMessage }
        }
      });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Fetch Tasks'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Se ha excedido el límite de reintentos');
      }, { timeout: 10000 });
    });
  });

  describe('createTask', () => {
    test('debe crear tarea exitosamente', async () => {
      const taskData = { title: 'New Task', description: 'Test' };
      const mockTask = { id: 3, ...taskData, completed: false };
      
      taskService.createTask.mockResolvedValue(mockTask);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Create Task'));

      await waitFor(() => {
        expect(taskService.createTask).toHaveBeenCalledWith(taskData);
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify([mockTask]));
      });
    });

    test('debe manejar error al crear tarea', async () => {
      const errorMessage = 'Title is required';
      taskService.createTask.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Create Task'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });
  });

  describe('updateTask', () => {
    test('debe actualizar tarea exitosamente', async () => {
      const initialTasks = [{ id: 1, title: 'Original Task', completed: false }];
      const updatedTask = { id: 1, title: 'Updated Task', completed: false };
      
      taskService.updateTask.mockResolvedValue(updatedTask);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      // Primero crear una tarea
      taskService.createTask.mockResolvedValue(initialTasks[0]);
      const user = userEvent.setup();
      await user.click(screen.getByText('Create Task'));

      await waitFor(() => {
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(initialTasks));
      });

      // Luego actualizar la tarea
      await user.click(screen.getByText('Update Task'));

      await waitFor(() => {
        expect(taskService.updateTask).toHaveBeenCalledWith(1, { title: 'Updated Task' });
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify([updatedTask]));
      });
    });

    test('debe manejar error al actualizar tarea', async () => {
      const errorMessage = 'Task not found';
      taskService.updateTask.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Update Task'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });
  });

  describe('deleteTask', () => {
    test('debe eliminar tarea exitosamente', async () => {
      const initialTasks = [{ id: 1, title: 'Task to delete', completed: false }];
      
      taskService.deleteTask.mockResolvedValue();

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      // Primero crear una tarea
      taskService.createTask.mockResolvedValue(initialTasks[0]);
      const user = userEvent.setup();
      await user.click(screen.getByText('Create Task'));

      await waitFor(() => {
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(initialTasks));
      });

      // Luego eliminar la tarea
      await user.click(screen.getByText('Delete Task'));

      await waitFor(() => {
        expect(taskService.deleteTask).toHaveBeenCalledWith(1);
        expect(screen.getByTestId('tasks')).toHaveTextContent('[]');
      });
    });

    test('debe manejar error al eliminar tarea', async () => {
      const errorMessage = 'Task not found';
      taskService.deleteTask.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      await user.click(screen.getByText('Delete Task'));

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });
  });

  describe('toggleTaskStatus', () => {
    test('debe cambiar estado de tarea exitosamente', async () => {
      const initialTasks = [{ id: 1, title: 'Task', completed: false }];
      const updatedTask = { id: 1, title: 'Task', completed: true };
      
      taskService.updateTask.mockResolvedValue(updatedTask);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      // Primero crear una tarea
      taskService.createTask.mockResolvedValue(initialTasks[0]);
      const user = userEvent.setup();
      await user.click(screen.getByText('Create Task'));

      await waitFor(() => {
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify(initialTasks));
      });

      // Luego cambiar el estado
      await user.click(screen.getByText('Toggle Status'));

      await waitFor(() => {
        expect(taskService.updateTask).toHaveBeenCalledWith(1, { completado: true });
        expect(screen.getByTestId('tasks')).toHaveTextContent(JSON.stringify([updatedTask]));
      });
    });
  });

  describe('clearError', () => {
    test('debe limpiar el error', async () => {
      const errorMessage = 'Test error';
      taskService.getTasks.mockRejectedValue({ response: { data: { detail: errorMessage } } });

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      
      // Primero generar un error
      await user.click(screen.getByText('Fetch Tasks'));
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

  describe('Rate limiting', () => {
    test('debe limitar peticiones a 1 por segundo', async () => {
      const mockResponse = {
        items: [{ id: 1, title: 'Task', completed: false }],
        total: 1,
        page: 1,
        size: 10,
        pages: 1
      };
      
      taskService.getTasks.mockResolvedValue(mockResponse);

      render(
        <TaskProvider>
          <TestComponent />
        </TaskProvider>
      );

      const user = userEvent.setup();
      
      // Hacer dos peticiones rápidamente
      await user.click(screen.getByText('Fetch Tasks'));
      await user.click(screen.getByText('Fetch Tasks'));

      // La segunda petición debería esperar
      await waitFor(() => {
        expect(taskService.getTasks).toHaveBeenCalledTimes(2);
      }, { timeout: 3000 });
    });
  });
}); 