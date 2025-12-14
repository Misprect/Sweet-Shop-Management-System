// src/context/AuthContext.tsx

import React, { createContext, useState, useEffect } from 'react';
import api from '../api/index.ts'; // Your configured Axios instance
import { useNavigate } from 'react-router-dom';
import axios from 'axios'; // Import axios for error handling

// --- Type Definitions ---
interface User {
    email: string;
    id: number;
    is_admin: boolean;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    login: (email: string, password: string, redirectPath?: string) => Promise<void>; 
    logout: () => void;
    // CRITICAL: Added the register function type
    register: (email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// --- Auth Provider Component ---

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // 1. Initial Load: Check localStorage for token
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            fetchUser(storedToken); 
        } else {
            setLoading(false);
        }
    }, []);

    // 2. Fetch User Details based on Token
    const fetchUser = async (authToken: string) => {
        try {
            api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
            const response = await api.get<User>('/users/me'); 
            
            setUser(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Token validation failed, logging out.', error);
            clearAuthData();
            setLoading(false);
            if (window.location.pathname !== '/login') {
                 navigate('/login', { replace: true });
            }
        }
    };
    
    // 3. Clear all auth data
    const clearAuthData = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        delete api.defaults.headers.common['Authorization'];
    };

    // 4. Login function
    const login = async (email: string, password: string, redirectPath: string = '/') => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            // CORRECTED PATH
            const tokenResponse = await api.post('/auth/token', formData.toString(), { 
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            
            const authToken = tokenResponse.data.access_token; 

            localStorage.setItem('token', authToken);
            setToken(authToken);
            await fetchUser(authToken);

            navigate(redirectPath, { replace: true });

        } catch (err) {
            if (axios.isAxiosError(err) && err.response) {
                // Throw the error response for the LoginForm to catch
                throw err.response.data.detail || "Authentication failed.";
            }
            throw "An unexpected error occurred during login.";
        }
    };

    // 5. Register function
    const register = async (email: string, password: string) => {
        try {
            // CORRECTED PATH
            await api.post('/auth/register', {
                email: email,
                password: password,
            });
            
            // On successful registration, immediately call login to get the token 
            // and redirect to the dashboard.
            await login(email, password, '/');
            
        } catch (err) {
            // START OF CRITICAL ERROR HANDLING FIX
            let errorMessage = "An unexpected error occurred during registration.";
        
            if (axios.isAxiosError(err) && err.response) {
                
                // 422 Unprocessable Entity (FastAPI Validation Error)
                if (err.response.status === 422 && err.response.data && err.response.data.detail) {
                    const details = err.response.data.detail;
                    if (Array.isArray(details) && details.length > 0 && details[0].msg) {
                        // Extract the first human-readable validation message
                        errorMessage = `Validation Error: ${details[0].msg}`;
                    } else {
                        errorMessage = "Invalid data submitted.";
                    }
                } 
                // Handle other standard API errors (e.g., 400 Bad Request: "Email already registered")
                else if (err.response.data && err.response.data.detail) {
                    errorMessage = err.response.data.detail;
                }
            } 
            
            // THROW SIMPLE STRING: This resolves the React runtime error.
            throw errorMessage;
        }
    };
    
    // 6. Logout function
    const logout = () => {
        clearAuthData();
        navigate('/login');
    };

    const contextValue: AuthContextType = {
        user,
        token,
        isAuthenticated: !!token && !!user,
        login,
        logout,
        // CRITICAL: Export the register function
        register,
    };

    if (loading) {
        return <div className="text-center mt-5">Loading session...</div>;
    }

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
};

export { AuthContext };