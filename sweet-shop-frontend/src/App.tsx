// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.tsx'; 
import useAuth from './hooks/useAuth.ts';

// Components
import Navbar from './components/layout/Navbar.tsx'; 
import LoginForm from './components/Auth/LoginForm.tsx';
import RegisterForm from './components/Auth/RegisterForm.tsx'; 
import Dashboard from './components/Dashboard.tsx';
import SweetListAdmin from './components/Admin/SweetListAdmin.tsx';
import SweetForm from './components/Admin/SweetForm.tsx';
import OrderListAdmin from './components/Admin/OrderListAdmin.tsx'; 
import UserListAdmin from './components/Admin/UserListAdmin.tsx'; // FINAL ADMIN IMPORT

// --- Helper Component: PrivateRoute (Requires Login) ---
const PrivateRoute = ({ element }: { element: React.ReactNode }) => {
    const { isAuthenticated, user } = useAuth(); 
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }
    return element;
};

// --- Helper Component: AdminRoute (Requires Login AND Admin status) ---
const AdminRoute = ({ element }: { element: React.ReactNode }) => {
    const { isAuthenticated, user } = useAuth();
    
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }
    
    // Check if the user is an admin
    if (!user || !user.is_admin) {
        return <Navigate to="/" replace />; // Redirect non-admins to the Dashboard
    }
    
    return element;
};


const App: React.FC = () => {
    return (
        <Router>
            <AuthProvider>
                <Navbar /> 
                <main className="container-fluid py-4">
                    <Routes>
                        {/* --------------------------- */}
                        {/* 1. PUBLIC ROUTES (Auth)     */}
                        {/* --------------------------- */}
                        <Route path="/login" element={<LoginForm />} />
                        <Route path="/register" element={<RegisterForm />} />
                        
                        {/* --------------------------- */}
                        {/* 2. PRIVATE ROUTES (Customer View) */}
                        {/* --------------------------- */}
                        <Route 
                            path="/" 
                            element={<PrivateRoute element={<Dashboard />} />} 
                        />
                        
                        {/* --------------------------- */}
                        {/* 3. ADMIN ROUTES (Management)*/}
                        {/* --------------------------- */}
                        
                        {/* Product Management */}
                        <Route 
                            path="/admin/sweets" 
                            element={<AdminRoute element={<SweetListAdmin />} />} 
                        />
                        <Route 
                            path="/admin/sweets/new" 
                            element={<AdminRoute element={<SweetForm />} />} 
                        />
                        <Route 
                            path="/admin/sweets/edit/:id" 
                            element={<AdminRoute element={<SweetForm />} />} 
                        />
                        
                        {/* Order Management */}
                        <Route
                            path="/admin/orders"
                            element={<AdminRoute element={<OrderListAdmin />} />}
                        />

                        {/* User Management (The final piece) */}
                        <Route
                            path="/admin/users"
                            element={<AdminRoute element={<UserListAdmin />} />}
                        />

                        {/* Fallback route - Redirect any unknown path to the default protected route */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </AuthProvider>
        </Router>
    );
};

export default App;