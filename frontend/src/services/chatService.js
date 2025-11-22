import api from './authService';

export const chatService = {
  async startConversation(orderType = 'general') {
    const response = await api.post('/chat/message/', { order_type: orderType });
    return response.data;
  },

  async sendMessage(conversationId, message, context = {}) {
    const response = await api.post('/chat/message/', {
      conversation_id: conversationId,
      message,
      context,
    });
    return response.data;
  },

  async getChatHistory(conversationId) {
    const response = await api.get(`/chat/history/?conversation_id=${conversationId}`);
    return response.data;
  },

  async endConversation(conversationId) {
    const response = await api.post(`/order/conversations/${conversationId}/end/`);
    return response.data;
  },

  async uploadVoiceRecording(audioFile, durationSeconds) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    if (typeof durationSeconds === 'number' && !Number.isNaN(durationSeconds)) {
      formData.append('duration', durationSeconds.toString());
    }
    
    const response = await api.post('/chat/voice/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async processMessage(message, context = {}) {
    const response = await api.post('/order/ai/process-message/', {
      message,
      context,
    });
    return response.data;
  },

  async generateAIResponse(prompt, model = 'gpt-3.5-turbo') {
    const response = await api.post('/order/ai/generate-response/', {
      prompt,
      model,
    });
    return response.data;
  },
};