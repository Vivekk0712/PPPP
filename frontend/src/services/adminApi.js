import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000';

const adminApi = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true
});

export const getAdminStats = () => {
  return adminApi.get('/api/admin/stats');
};

export const getAllUsers = () => {
  return adminApi.get('/api/admin/users');
};

export const getAllProjects = (limit = 50) => {
  return adminApi.get('/api/admin/projects', { params: { limit } });
};

export const getAllLogs = (limit = 100) => {
  return adminApi.get('/api/admin/logs', { params: { limit } });
};
