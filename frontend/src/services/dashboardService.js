import api from './authService';

export const dashboardService = {
  async getStats() {
    const response = await api.get('/core/dashboard/stats/');
    return response.data;
  },

  async getSystemHealth() {
    const response = await api.get('/core/system/health/');
    return response.data;
  },

  async getNotifications() {
    const response = await api.get('/core/notifications/');
    return response.data;
  },

  async markNotificationAsRead(notificationId) {
    const response = await api.post(`/core/notifications/${notificationId}/read/`);
    return response.data;
  },

  async getRecentActivity(limit = 10) {
    const response = await api.get('/analytics/activities/', {
      params: { limit }
    });
    return response.data;
  },

  async getUserStats() {
    const response = await api.get('/analytics/users/stats/');
    return response.data;
  },

  async getOrderStats() {
    const response = await api.get('/analytics/orders/stats/');
    return response.data;
  },

  async getConversationStats() {
    const response = await api.get('/analytics/conversations/stats/');
    return response.data;
  },
};