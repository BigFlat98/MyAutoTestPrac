import axios from 'axios';

// Create an Axios instance with a configuration
const api = axios.create({
    // Use VITE_API_BASE_URL from environment variables, or default to localhost
    // Use relative path for Nginx reverse proxy
    baseURL: '/api',
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

const chat = axios.create({
    baseURL: '/chat',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
})

export { api, chat };

// Authentication API
export const login = (data) => api.post('/auth/login', data);
export const signup = (data) => api.post('/auth/signup', data);
export const logout = () => api.post('/auth/logout');
