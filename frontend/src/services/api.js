import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await api.post('/refresh', {
            token: refreshToken
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Si el refresh token también expiró, redirigir al login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/register', userData);
    return response.data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await api.post('/logout', { token: refreshToken });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/me');
    return response.data;
  },

  logoutAll: async () => {
    await api.post('/logout/all');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Servicios de tareas
export const taskService = {
  getTasks: async (params = {}) => {
    console.log('API: Enviando petición GET /tareas con params:', params);
    const response = await api.get('/tareas', { params });
    console.log('API: Respuesta de getTasks:', response.data);
    return response.data;
  },

  getTask: async (id) => {
    const response = await api.get(`/tareas/${id}`);
    return response.data;
  },

  createTask: async (taskData) => {
    console.log('API: Enviando petición POST /tareas con datos:', taskData);
    const response = await api.post('/tareas', taskData);
    console.log('API: Respuesta de crear tarea:', response.data);
    return response.data;
  },

  updateTask: async (id, taskData) => {
    const response = await api.put(`/tareas/${id}`, taskData);
    return response.data;
  },

  deleteTask: async (id) => {
    await api.delete(`/tareas/${id}`);
  },
};

// Servicios de contraseñas
export const passwordService = {
  getRequirements: async () => {
    const response = await api.get('/password/requirements');
    return response.data;
  },

  checkStrength: async (password) => {
    const response = await api.post('/password/check-strength', { password });
    return response.data;
  },

  validate: async (password) => {
    const response = await api.post('/password/validate', { password });
    return response.data;
  },
};

export default api; 