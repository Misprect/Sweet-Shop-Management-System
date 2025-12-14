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
            const tokenResponse = await api.post('/token', formData.toString(), {
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

    // 5. Register function - CRITICAL ADDITION
    const register = async (email: string, password: string) => {
        try {
            // Registration endpoint /api/register expects JSON data
            // Note: The FastAPI backend will handle the /api prefix correctly
            await api.post('/register', {
                email: email,
                password: password,
            });
            
            // On successful registration, immediately call login to get the token 
            // and redirect to the dashboard.
            await login(email, password, '/');
            
        } catch (err) {
            // Re-throw the error so RegisterForm can catch it and display the message
            throw err;
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