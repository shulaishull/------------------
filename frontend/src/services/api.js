import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth endpoints
export const login = (username, password) => {
  return api.post('/auth/login', { username, password });
};

// File endpoints
export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Comparison endpoints
export const compareFiles = (data) => {
  return api.post('/compare', data);
};

// Script endpoints
export const getScripts = (params) => {
  return api.get('/scripts', { params });
};

export const getScript = (id) => {
  return api.get(`/scripts/${id}`);
};

export const createScript = (data) => {
  return api.post('/scripts', data);
};

export const updateScript = (id, data) => {
  return api.put(`/scripts/${id}`, data);
};

export const deleteScript = (id) => {
  return api.delete(`/scripts/${id}`);
};

// Comparison template endpoints
export const getComparisons = (params) => {
  return api.get('/comparisons', { params });
};

export const getComparison = (id) => {
  return api.get(`/comparisons/${id}`);
};

export const createComparison = (data) => {
  return api.post('/comparisons', data);
};

export const updateComparison = (id, data) => {
  return api.put(`/comparisons/${id}`, data);
};

export const deleteComparison = (id) => {
  return api.delete(`/comparisons/${id}`);
};

export default api;