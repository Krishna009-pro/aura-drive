import axios from 'axios';

const api = axios.create({
  baseURL: '/',
});

// Automatically add the JWT token to every request if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aura_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/jwt/login', formData);
  },
  register: (email, password) => {
    return api.post('/auth/register', { email, password });
  },
  me: () => api.get('/users/me')
};

export const driveApi = {
  // mode can be 'private' (default) or 'public'
  getFeed: (mode = 'private') => api.get(`/feed?mode=${mode}`),
  
  upload: (file, caption, isPublic = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', caption);
    formData.append('is_public', isPublic); // New field for visibility
    return api.post('/uploadfile', formData);
  },
  
  deletePost: (id) => api.delete(`/posts/${id}`)
};

export default api;
