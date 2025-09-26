import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for AI processing and bulk operations
});

// Add request interceptor to include auth token
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

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Check if this is a cleaning request or management request
      const isCleaningRequest = error.config?.url?.includes('/cleaning');
      window.location.href = isCleaningRequest ? '/login' : '/management/login';
    }
    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/api/auth/login', { username, password });
    return response.data;
  },
  
  logout: async () => {
    await api.post('/api/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  
  getAvailableUsers: async () => {
    const response = await api.get('/api/auth/users/list');
    return response.data;
  }
};

// Trainset API functions
export const trainsetAPI = {
  getInductionPlan: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.post('/api/induction/plan', params);
    return response.data;
  },
  
  getFleetStatus: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/fleet/status', { params });
    return response.data;
  },
  
  getAllTrainsets: async () => {
    const response = await api.get('/api/trainsets');
    return response.data;
  },
  
  getTrainsetDetail: async (trainsetId) => {
    const response = await api.get(`/api/trainsets/${trainsetId}`);
    return response.data;
  },
  
  getTrainsetByNumber: async (trainsetNumber) => {
    const response = await api.get(`/api/trainsets/number/${trainsetNumber}`);
    return response.data;
  },
  
  getTrainsetEvaluation: async (trainsetId, date = null) => {
    const params = date ? { date } : {};
    const response = await api.get(`/api/trainsets/${trainsetId}/evaluation`, { params });
    return response.data;
  },
  
  // Trainset Management Functions
  createTrainset: async (trainsetData) => {
    const response = await api.post('/api/trainsets', trainsetData);
    return response.data;
  },
  
  updateTrainset: async (trainsetId, trainsetData) => {
    const response = await api.put(`/api/trainsets/${trainsetId}`, trainsetData);
    return response.data;
  },
  
  deleteTrainset: async (trainsetId) => {
    const response = await api.delete(`/api/trainsets/${trainsetId}`);
    return response.data;
  },
  
  generateDummyTrainsets: async (numTrainsets = 5, prefix = 'TS') => {
    const response = await api.post(`/api/trainsets/generate-dummy?num_trainsets=${numTrainsets}&prefix=${prefix}`);
    return response.data;
  }
};

// Utility functions
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
  }
};

export const getAuthToken = () => {
  return localStorage.getItem('token');
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

export default api;