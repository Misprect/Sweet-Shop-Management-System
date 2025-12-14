// src/components/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth.ts';
import api from '../api/index.ts'; 
// Import the components (assuming these files exist now or will be created next)
import SweetCard from './SweetCard.tsx'; 
import CartSummary from './CartSummary.tsx'; 

// --- Interface Definitions ---

// Define the User structure to get the email property
interface User {
    email: string;
    id: number;
    is_admin: boolean;
}

// Interface for the sweet/product data fetched from the backend
interface Sweet {
    id: number;
    name: string;
    description: string;
    category: string;
    price: number;
    stock_quantity: number;
    is_available: boolean;
}

// Interface for items stored in the local cart state
export interface CartItem { // Exported for use in CartSummary.tsx
    sweet_id: number;
    name: string;
    price_at_purchase: number;
    quantity: number;
}


const Dashboard: React.FC = () => {
    // Cast user type for safety, assuming useAuth is correctly defined
    const { user, token } = useAuth() as { user: User | null, token: string | null }; 
    
    const [sweets, setSweets] = useState<Sweet[]>([]);
    const [cart, setCart] = useState<CartItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchSweets = async () => {
        try {
            setLoading(true);
            const response = await api.get<Sweet[]>('/sweets/');
            setSweets(response.data);
            setError(''); // Clear error on success
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
                // Find the current actual stock quantity from the sweets list
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
            
            // Note: Axios automatically adds the auth header if configured in api/index.ts.
            // Explicitly defining it is redundant but harmless.
            await api.post('/orders/', orderData); 
            
            alert('Order successfully placed! Your cart has been cleared.');
            setCart([]); 
            
            // Refresh the sweet list to update stock counts (CRITICAL STEP)
            fetchSweets(); 

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
            
            <div className="row">
                {/* Product List Column */}
                <div className="col-md-8">
                    <h3 className="mb-3">Our Sweets</h3>
                    <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                        {sweets
                            .filter(sweet => sweet.is_available) // Only show available sweets
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
        </div>
    );
};

export default Dashboard;