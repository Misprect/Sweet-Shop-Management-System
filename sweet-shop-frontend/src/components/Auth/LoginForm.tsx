// src/components/Auth/LoginForm.tsx

import React, { useState } from 'react';
import useAuth from '../../hooks/useAuth.ts';
import { useNavigate, Link } from 'react-router-dom'; // Added Link import

const LoginForm: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    
    // Get the login function from the context
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null); // Clear previous errors

        try {
            // CRITICAL: Call the updated login function with email and password
            await login(email, password);
            
            // On successful login, AuthContext handles navigation (optional: navigate('/'))
            // If AuthContext handles navigation, this line might be redundant:
            // navigate('/'); 

        } catch (err: any) {
            // Display the error message thrown by AuthContext
            // Handle both string and Axios error structure
            const errorMessage = typeof err === 'string' 
                ? err 
                : err.response?.data?.detail || 'Login failed. Please check your credentials.';
            setError(errorMessage);
        }
    };

    return (
        <div className="row justify-content-center mt-5">
            <div className="col-md-6 col-lg-4">
                <div className="card shadow-lg">
                    <div className="card-header bg-primary text-white text-center">
                        <h3 className="mb-0">Customer Login</h3>
                    </div>
                    <div className="card-body">
                        {error && (
                            <div className="alert alert-danger" role="alert">
                                {error}
                            </div>
                        )}
                        <form onSubmit={handleSubmit}>
                            {/* ... (Email and Password input fields remain the same) ... */}
                            <div className="mb-3">
                                <label htmlFor="emailInput" className="form-label">Email address</label>
                                <input
                                    type="email"
                                    className="form-control"
                                    id="emailInput"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="passwordInput" className="form-label">Password</label>
                                <input
                                    type="password"
                                    className="form-control"
                                    id="passwordInput"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100">
                                Log In
                            </button>
                        </form>
                    </div>
                    <div className="card-footer text-center">
                        <p className="mb-0">
                            Don't have an account? <Link to="/register">Register here</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginForm;