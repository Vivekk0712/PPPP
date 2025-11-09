import axios from 'axios';

const mlApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

// ML Project endpoints
export const createMLProject = (message) => {
  return mlApi.post('/api/ml/chat', { message });
};

export const getMLProjects = () => {
  return mlApi.get('/api/ml/projects');
};

export const getMLProjectById = (projectId) => {
  return mlApi.get(`/api/ml/projects/${projectId}`);
};

export const getProjectLogs = (projectId) => {
  return mlApi.get(`/api/ml/projects/${projectId}/logs`);
};

export const downloadModel = (projectId) => {
  return mlApi.get(`/api/ml/projects/${projectId}/download`, {
    responseType: 'blob'
  });
};

export const testModel = (projectId, imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  return mlApi.post(`/api/ml/projects/${projectId}/test`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export default mlApi;
