import api from './authService';

export const adminService = {
  async getUsers() {
    const response = await api.get('/admin/users/');
    return response.data;
  },
  
  async createUser(payload) {
    const response = await api.post('/admin/users/', payload);
    return response.data;
  },
  
  async updateUser(userId, payload) {
    const response = await api.put(`/admin/users/${userId}/`, payload);
    return response.data;
  },
  
  async deleteUser(userId) {
    const response = await api.delete(`/admin/users/${userId}/`);
    return response.data;
  },
  
  async getAnalytics() {
    const response = await api.get('/admin/analytics/');
    return response.data;
  },
};

