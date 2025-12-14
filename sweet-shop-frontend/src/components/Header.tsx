// src/components/Header.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth.ts'; 

const Header: React.FC = () => {
    const { isAuthenticated, logout, user } = useAuth();

    return (
        <header className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
            <div className="container-fluid">
                <Link className="navbar-brand" to="/">Sweet Shop</Link>
                <div className="d-flex">
                    {isAuthenticated ? (
                        <>
                            <span className="navbar-text me-3">
                                Welcome, {user?.email || 'User'}!
                            </span>
                            {user?.is_admin && (
                                <Link className="btn btn-warning me-2" to="/admin/sweets">Admin</Link>
                            )}
                            <button 
                                className="btn btn-outline-light" 
                                onClick={logout}
                            >
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link className="btn btn-outline-light me-2" to="/login">Login</Link>
                            <Link className="btn btn-light" to="/register">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;