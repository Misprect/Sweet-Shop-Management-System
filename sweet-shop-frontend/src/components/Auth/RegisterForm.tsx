// src/components/Auth/RegisterForm.tsx

import React, { useState } from 'react';
import useAuth from '../../hooks/useAuth.ts'; // Corrected path
import { useNavigate } from 'react-router-dom';

const RegisterForm: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    
    // Get the register function from the context
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null); 
        setSuccessMessage(null);

        try {
            // Call the register function provided by AuthContext
            await register(email, password);
            
            // Note: AuthContext already calls login and navigates on success, 
            // so this success message and timeout are now redundant but kept for now.
            setSuccessMessage('Registration successful! Redirecting...');

        } catch (err: any) {
            // --- FIX APPLIED HERE ---
            // AuthContext now throws a string, so we must check for that type.
            
            let errorMessage = 'Registration failed. Please check your network connection.';
            
            // If the thrown error is a string (from AuthContext, e.g., "Validation Error: field required")
            if (typeof err === 'string') {
                errorMessage = err;
            } 
            // Fallback for unexpected structured errors (less likely now)
            else if (err.response?.data?.detail) {
                errorMessage = err.response.data.detail;
            }
            
            setError(errorMessage);
        }
    };

    return (
        <div className="row justify-content-center mt-5">
            <div className="col-md-6 col-lg-4">
                <div className="card shadow-lg">
                    <div className="card-header bg-success text-white text-center">
                        <h3 className="mb-0">Customer Registration</h3>
                    </div>
                    <div className="card-body">
                        {error && (
                            <div className="alert alert-danger" role="alert">
                                **Error:** {error}
                            </div>
                        )}
                        {successMessage && (
                            <div className="alert alert-success" role="alert">
                                {successMessage}
                            </div>
                        )}
                        <form onSubmit={handleSubmit}>
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
                            <button type="submit" className="btn btn-success w-100">
                                Register
                            </button>
                        </form>
                    </div>
                    <div className="card-footer text-center">
                        <p className="mb-0">
                            Already have an account? <a href="/login">Login here</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegisterForm;