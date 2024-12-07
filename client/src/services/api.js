import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  withCredentials: true
});

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
        const { access_token } = response.data;

        localStorage.setItem('token', access_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const handleApiError = (error) => {
  if (error.response) {
    return error.response.data.detail || 'An error occurred';
  }
  if (error.request) {
    return 'No response from server';
  }
  return 'Request failed';
};

export default api;