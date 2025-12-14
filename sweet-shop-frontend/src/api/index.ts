// src/api/index.ts
import axios from 'axios';

// Define the base URL of your FastAPI backend.
// This MUST match the address where your backend server is running.
const API_BASE_URL = 'http://127.0.0.1:8000/api'; 

// Create an Axios instance with default settings
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- Interceptor to attach the JWT Token ---
// This ensures that all authenticated API calls (like /orders/ or /users/me) 
// automatically include the 'Authorization' header.
api.interceptors.request.use(
    config => {
        // We read the token directly from localStorage since it's the source of truth
        const token = localStorage.getItem('token'); 
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        } else {
             // Ensure the header is not sent if no token exists
             delete config.headers.Authorization;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// We export this 'api' instance so that all other files (AuthContext, Dashboard) 
// can import and use it.
export default api;