import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';
import { authState } from '../contexts/AuthContext';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token dynamically
api.interceptors.request.use(
  (config) => {
    const token = authState?.user?.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    if (status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
