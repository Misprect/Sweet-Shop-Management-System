// src/components/Layout/Navbar.tsx

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth.ts'; // Import the Auth hook

const Navbar: React.FC = () => {
    // Get authentication state and functions
    const { isAuthenticated, user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login'); // Redirect to login page after logout
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
            <div className="container-fluid">
                {/* Brand/App Name */}
                <Link className="navbar-brand fw-bold" to="/">
                    🍬 Sweet Shop Admin
                </Link>
                
                {/* Toggler button for mobile */}
                <button 
                    className="navbar-toggler" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" 
                    aria-expanded="false" 
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        {/* Always show Dashboard link for logged-in users */}
                        {isAuthenticated && (
                            <li className="nav-item">
                                <Link className="nav-link" to="/">
                                    Dashboard
                                </Link>
                            </li>
                        )}

                        {/* --- ADMIN LINKS (Only visible if user is an Admin) --- */}
                        {user?.is_admin && (
                            <>
                                <li className="nav-item dropdown">
                                    <a 
                                        className="nav-link dropdown-toggle" 
                                        href="#" 
                                        id="adminDropdown" 
                                        role="button" 
                                        data-bs-toggle="dropdown" 
                                        aria-expanded="false"
                                    >
                                        Admin Management
                                    </a>
                                    <ul className="dropdown-menu" aria-labelledby="adminDropdown">
                                        <li>
                                            <Link className="dropdown-item" to="/admin/sweets">
                                                Manage Sweets
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/admin/orders">
                                                Manage Orders
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/admin/users">
                                                Manage Users
                                            </Link>
                                        </li>
                                    </ul>
                                </li>
                            </>
                        )}
                    </ul>

                    {/* --- RIGHT SIDE: Auth/Logout Links --- */}
                    <ul className="navbar-nav">
                        {isAuthenticated ? (
                            <>
                                <li className="nav-item">
                                    <span className="nav-link text-warning">
                                        Logged in as: {user.email}
                                    </span>
                                </li>
                                <li className="nav-item">
                                    <button 
                                        className="btn btn-outline-light ms-2"
                                        onClick={handleLogout}
                                    >
                                        Logout
                                    </button>
                                </li>
                            </>
                        ) : (
                            <>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/login">
                                        Login
                                    </Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="btn btn-outline-light" to="/register">
                                        Register
                                    </Link>
                                </li>
                            </>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;