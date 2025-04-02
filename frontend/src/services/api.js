// File: frontend/src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
});

// Add interceptor to include auth token in requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth services
export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await api.post('/auth/token', formData);
  return response.data;
};

export const register = async (email, password) => {
  const response = await api.post('/auth/register', { email, password });
  return response.data;
};

// Invoice services
export const getInvoices = async () => {
  const response = await api.get('/invoices/');
  return response.data;
};

export const getInvoice = async (id) => {
  const response = await api.get(`/invoices/${id}`);
  return response.data;
};

export const uploadInvoice = async (file, metadata = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('invoice_data', JSON.stringify(metadata));
  
  const response = await api.post('/invoices/', formData);
  return response.data;
};

export const updateInvoice = async (id, data) => {
  const response = await api.put(`/invoices/${id}`, data);
  return response.data;
};

export const deleteInvoice = async (id) => {
  const response = await api.delete(`/invoices/${id}`);
  return response.data;
};

export default api;