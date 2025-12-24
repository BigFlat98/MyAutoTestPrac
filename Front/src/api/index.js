import axios from 'axios';

// Create an Axios instance with a configuration
const api = axios.create({
    // Use VITE_API_BASE_URL from environment variables, or default to localhost
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
