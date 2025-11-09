import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

export const sessionLogin = (idToken) => {
  return api.post('/api/sessionLogin', { idToken });
};

export const sessionLogout = () => {
  return api.post('/api/sessionLogout');
};

export const getMe = () => {
  return api.get('/api/me');
};

export const getHistory = () => {
  return api.get('/api/history');
};

export const sendMessage = (message, metadata) => {
  return api.post('/api/chat', { message, metadata });
};

export const clearChat = () => {
  return api.delete('/api/clear-chat');
};

export default api;
