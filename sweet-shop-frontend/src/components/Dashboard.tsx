// src/components/Dashboard.tsx (FINAL INTEGRATION)

import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth.ts';
import api from '../api/index.ts'; 

// 1. IMPORT ADMIN COMPONENTS
import CreateSweetForm from './Admin/CreateSweetForm.tsx'; 
import OrderListAdmin from './Admin/OrderListAdmin.tsx'; // <-- NEW IMPORT
// 2. IMPORT USER COMPONENTS
import OrderHistory from './User/OrderHistory.tsx'; 

import SweetCard from './SweetCard.tsx'; 
import CartSummary from './CartSummary.tsx'; 

// --- Interface Definitions ---

interface User {
    email: string;
    id: number;
    is_admin: boolean;
}

interface Sweet {
    id: number;
    name: string;
    description: string;
    category: string;
    price: number;
    stock_quantity: number;
    is_available: boolean;
}

export interface CartItem { 
    sweet_id: number;
    name: string;
    price_at_purchase: number;
    quantity: number;
}

// Define possible views (UPDATED)
type DashboardView = 'shop' | 'orders' | 'admin-orders'; 

const Dashboard: React.FC = () => {
    const { user, token } = useAuth() as { user: User | null, token: string | null }; 
    
    const [sweets, setSweets] = useState<Sweet[]>([]);
    const [cart, setCart] = useState<CartItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    const [currentView, setCurrentView] = useState<DashboardView>('shop'); 
    const [showAdminForm, setShowAdminForm] = useState(false);

    const fetchSweets = async () => {
        try {
            setLoading(true);
            const response = await api.get<Sweet[]>('/sweets/');
            setSweets(response.data);
            setError(''); 
        } catch (err) {
            setError('Failed to fetch sweets. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSweets();
    }, []);

    const addToCart = (sweet: Sweet) => {
        setCart(prevCart => {
            const existingItem = prevCart.find(item => item.sweet_id === sweet.id);

            if (existingItem) {
                const sweetData = sweets.find(s => s.id === sweet.id);
                const originalStock = sweetData ? sweetData.stock_quantity : existingItem.quantity;
                const newQuantity = existingItem.quantity + 1;
                
                if (newQuantity > originalStock) {
                    alert(`Cannot add more than the available stock (${originalStock}) for ${sweet.name}.`);
                    return prevCart;
                }
                
                return prevCart.map(item =>
                    item.sweet_id === sweet.id ? { ...item, quantity: newQuantity } : item
                );
            } else {
                if (sweet.stock_quantity > 0) {
                    return [...prevCart, {
                        sweet_id: sweet.id,
                        name: sweet.name,
                        price_at_purchase: sweet.price,
                        quantity: 1
                    }];
                } else {
                    alert(`${sweet.name} is currently out of stock.`);
                    return prevCart;
                }
            }
        });
    };

    const placeOrder = async () => {
        if (cart.length === 0) {
            alert('Your cart is empty! Add items before placing an order.');
            return;
        }

        const orderData = {
            items: cart.map(item => ({
                sweet_id: item.sweet_id,
                quantity: item.quantity
            }))
        };
        
        try {
            if (!token) {
                alert("Session expired. Please log in again."); 
                return;
            }
            
            await api.post('/orders/', orderData); 
            
            alert('Order successfully placed! Your cart has been cleared.');
            setCart([]); 
            
            fetchSweets(); 

            setCurrentView('orders'); 

        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'An unexpected error occurred while placing the order.';
            alert(`Order Failed: ${errorMessage}`);
        }
    };

    if (loading) {
        return <div className="container mt-5 text-center">Loading sweet menu...</div>;
    }

    if (error) {
        return <div className="container mt-5 alert alert-danger">{error}</div>;
    }

    return (
        <div className="container mt-4">
            <h2 className="mb-4">
                Welcome to the Sweet Shop, {user ? user.email : 'Guest'}!
            </h2>
            
            {/* VIEW NAVIGATION BUTTONS */}
            <div className="mb-4 d-flex">
                <button 
                    className={`btn me-2 ${currentView === 'shop' ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setCurrentView('shop')}
                >
                    🛒 Sweet Shop
                </button>
                <button 
                    className={`btn ${currentView === 'orders' ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setCurrentView('orders')}
                >
                    🧾 My Orders
                </button>
            </div>
            {/* END VIEW NAVIGATION BUTTONS */}
            
            {/* ADMIN SECTION: Conditional rendering for admin tools */}
            {user?.is_admin && (
                <div className="mb-4 p-3 border rounded bg-light">
                    <h4 className="text-primary mb-3">Admin Panel</h4>

                    {/* --- ADMIN NAVIGATION BUTTONS --- */}
                    <div className="d-flex mb-3">
                        <button 
                            className={`btn me-2 ${currentView === 'shop' ? 'btn-primary' : 'btn-outline-primary'}`}
                            onClick={() => setCurrentView('shop')}
                        >
                            ⚙️ Admin Sweet Form
                        </button>
                        <button 
                            className={`btn me-2 ${currentView === 'admin-orders' ? 'btn-primary' : 'btn-outline-primary'}`}
                            onClick={() => setCurrentView('admin-orders')}
                        >
                            📋 Manage All Orders
                        </button>
                    </div>
                    
                    {/* Conditional Form Display (Only show form if in 'shop' view) */}
                    {currentView === 'shop' && (
                        <>
                        <button 
                            className={`btn mb-3 ${showAdminForm ? 'btn-warning' : 'btn-primary'}`}
                            onClick={() => setShowAdminForm(!showAdminForm)}
                        >
                            {showAdminForm ? 'Hide Sweet Creation Form' : 'Show Sweet Creation Form'}
                        </button>
                        
                        {showAdminForm && (
                            <CreateSweetForm 
                                onSweetCreated={fetchSweets} 
                            />
                        )}
                        </>
                    )}
                </div>
            )}
            {/* END ADMIN SECTION */}

            {/* CONDITIONAL CONTENT RENDERING */}
            {currentView === 'shop' && (
                <div className="row">
                    {/* Product List Column */}
                    <div className="col-md-8">
                        <h3 className="mb-3">Our Sweets</h3>
                        <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                            {sweets
                                .filter(sweet => sweet.is_available) 
                                .map(sweet => (
                                    <div className="col" key={sweet.id}>
                                        <SweetCard 
                                            sweet={sweet} 
                                            addToCart={addToCart} 
                                        />
                                    </div>
                                ))}
                            {sweets.length === 0 && (
                                <div className="col-12">
                                    <div className="alert alert-info text-center">
                                        No sweets are currently listed. 
                                        {user?.is_admin && " (Admin: Use the Sweet Form to add the first product.)"}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Cart Summary Column */}
                    <div className="col-md-4">
                        <CartSummary 
                            cart={cart} 
                            setCart={setCart} 
                            placeOrder={placeOrder} 
                        />
                    </div>
                </div>
            )}
            
            {/* USER ORDER HISTORY VIEW */}
            {currentView === 'orders' && (
                <OrderHistory sweets={sweets} /> 
            )}
            
            {/* ADMIN ORDER MANAGEMENT VIEW (NEW) */}
            {currentView === 'admin-orders' && user?.is_admin && (
                <OrderListAdmin /> 
            )}
            
        </div>
    );
};

export default Dashboard;