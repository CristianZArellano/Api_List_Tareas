import React, { createContext, useContext, useState } from 'react';
import { taskService } from '../services/api';

const TaskContext = createContext();

export { TaskContext };

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTasks debe ser usado dentro de un TaskProvider');
  }
  return context;
};

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastFetchTime, setLastFetchTime] = useState(0);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  });

  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const handleApiError = async (error, retryOperation) => {
    const errorMessage = error.response?.data?.detail || 'Error en la operación';
    
    if (error.response?.status === 429) { // Too Many Requests
      const retryAfter = error.response.headers['retry-after'] || 5;
      setError(`Demasiadas solicitudes. Reintentando en ${retryAfter} segundos...`);
      
      if (retryCount < 3) {
        setRetryCount(prev => prev + 1);
        await wait(retryAfter * 1000);
        return retryOperation();
      } else {
        setError('Se ha excedido el límite de reintentos. Por favor, espera un momento.');
        setRetryCount(0);
        throw new Error(errorMessage);
      }
    }
    
    setError(errorMessage);
    throw error;
  };

  const fetchTasks = async (params = {}) => {
    console.log('TaskContext: fetchTasks ejecutándose con params:', params);
    const now = Date.now();
    const timeSinceLastFetch = now - lastFetchTime;
    
    if (timeSinceLastFetch < 1000) { // Limitar a 1 solicitud por segundo
      console.log('TaskContext: Esperando antes de hacer nueva petición...');
      await wait(1000 - timeSinceLastFetch);
    }

    try {
      setLoading(true);
      setError(null);
      setLastFetchTime(Date.now());
      
      console.log('TaskContext: Llamando a taskService.getTasks...');
      const response = await taskService.getTasks(params).catch(error => {
        console.error('TaskContext: Error en taskService.getTasks:', error);
        return handleApiError(error, () => fetchTasks(params));
      });
      
      console.log('TaskContext: Respuesta de getTasks:', response);
      setTasks(response.items);
      setPagination({
        total: response.total,
        page: response.page,
        size: response.size,
        pages: response.pages
      });
      
      setRetryCount(0);
      return response;
    } catch (error) {
      console.error('TaskContext: Error final en fetchTasks:', error);
      if (!error.response?.status === 429) {
        const errorMessage = error.response?.data?.detail || 'Error al cargar tareas';
        setError(errorMessage);
      }
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (taskData) => {
    console.log('TaskContext: Creando tarea con datos:', taskData);
    try {
      setError(null);
      const newTask = await taskService.createTask(taskData).catch(error => {
        console.error('TaskContext: Error en taskService.createTask:', error);
        return handleApiError(error, () => createTask(taskData));
      });
      console.log('TaskContext: Tarea creada exitosamente:', newTask);
      setTasks(prevTasks => [newTask, ...prevTasks]);
      return { success: true, task: newTask };
    } catch (error) {
      console.error('TaskContext: Error final en createTask:', error);
      if (!error.response?.status === 429) {
        const errorMessage = error.response?.data?.detail || 'Error al crear tarea';
        setError(errorMessage);
      }
      return { success: false, error: error.message };
    }
  };

  const updateTask = async (id, taskData) => {
    try {
      setError(null);
      const updatedTask = await taskService.updateTask(id, taskData).catch(error =>
        handleApiError(error, () => updateTask(id, taskData))
      );
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === id ? updatedTask : task
        )
      );
      return { success: true, task: updatedTask };
    } catch (error) {
      if (!error.response?.status === 429) {
        const errorMessage = error.response?.data?.detail || 'Error al actualizar tarea';
        setError(errorMessage);
      }
      return { success: false, error: error.message };
    }
  };

  const deleteTask = async (id) => {
    try {
      setError(null);
      await taskService.deleteTask(id).catch(error =>
        handleApiError(error, () => deleteTask(id))
      );
      setTasks(prevTasks => prevTasks.filter(task => task.id !== id));
      return { success: true };
    } catch (error) {
      if (!error.response?.status === 429) {
        const errorMessage = error.response?.data?.detail || 'Error al eliminar tarea';
        setError(errorMessage);
      }
      return { success: false, error: error.message };
    }
  };

  const toggleTaskStatus = async (id, completed) => {
    return await updateTask(id, { completado: completed });
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    tasks,
    loading,
    error,
    pagination,
    fetchTasks,
    createTask,
    addTask: createTask,
    updateTask,
    deleteTask,
    toggleTaskStatus,
    clearError,
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
}; 