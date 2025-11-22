import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  },

  async logout(token) {
    const response = await api.post('/auth/logout/');
    return response.data;
  },

  async getCurrentUser(token) {
    const response = await api.get('/auth/me/');
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  async updateProfile(userData) {
    const response = await api.put('/auth/profile/update/', userData);
    return response.data;
  },

  async changePassword(passwordData) {
    const response = await api.post('/auth/password/change/', passwordData);
    return response.data;
  },

  async checkPermission(permission) {
    const response = await api.post('/auth/check-permission/', { permission });
    return response.data;
  },
};

export default api;