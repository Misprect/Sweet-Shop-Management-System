// src/components/User/OrderHistory.tsx

import React, { useState, useEffect } from 'react';
import api from '../../api/index.ts';
import { Order, OrderItem } from '../../types/Order.ts'; 

// --- PROP INTERFACES ---

// The structure of the Sweet item required for lookup
interface SweetLookup {
    id: number;
    name: string;
}

// Define the component's props, expecting the full list of sweets
interface OrderHistoryProps {
    sweets: SweetLookup[];
}

// 2. COMPONENT SIGNATURE UPDATED to accept props with a defensive default
const OrderHistory: React.FC<OrderHistoryProps> = ({ sweets = [] }) => {
    
    // STATE DEFINITIONS
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Function to find the sweet name from the passed-in list
    const getSweetName = (id: number): string => {
        // 'sweets' is guaranteed to be an array due to the `= []` in the signature
        const sweet = sweets.find(s => s.id === id);
        return sweet ? sweet.name : `Sweet ID: ${id}`; // Fallback to ID if name is not found
    };
    
    useEffect(() => {
        const fetchOrders = async () => {
            setLoading(true); 

            try {
                const response = await api.get<Order[]>('/orders/');
                
                // Defensive array assignment
                setOrders(response.data ?? []); 
                setError(null);
            } catch (err: any) {
                console.error("Failed to fetch orders:", err);
                const errorMessage = err.response?.data?.detail || err.message || 'Failed to load order history.';
                setError(errorMessage);
            } finally {
                setLoading(false);
            }
        };

        fetchOrders();
    }, []);

    if (loading) {
        return <div className="container mt-5 text-center"><p>Loading your order history...</p></div>;
    }

    if (error) {
        return <div className="container mt-5 alert alert-danger">**Error loading history:** {error}</div>;
    }

    return (
        <div className="container mt-5">
            <h2 className="mb-4">🛍️ Your Order History</h2>

            {(!orders || orders.length === 0) ? (
                <div className="alert alert-info">You have not placed any orders yet.</div>
            ) : (
                <div className="list-group">
                    
                    {orders.map((order) => (
                        <div key={order.id} className="card shadow mb-4">
                            <div className="card-header bg-success text-white">
                                <h5 className="mb-0">Order ID: **{order.id}**</h5>
                            </div>
                            <div className="card-body">
                                <p><strong>Date Placed:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
                                <p><strong>Status:</strong> {order.status}</p>
                                <p className="h4 text-end">**Total:** ₹{order.total_price.toFixed(2)}</p>

                                <h6 className="mt-4 border-bottom pb-2">Items Purchased:</h6>
                                <ul className="list-group list-group-flush">
                                    {/* FIX: Using 'order.items' to match the backend JSON response */}
                                    {order.items?.map((item: OrderItem, index: number) => (
                                        <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                                            <span>
                                                {/* FIX: Using getSweetName for display name */}
                                                **{getSweetName(item.sweet_id)}**
                                            </span>
                                            <span className="badge bg-secondary rounded-pill">Qty: {item.quantity}</span>
                                            <span className="fw-bold">
                                                Subtotal: ₹{(item.price_at_purchase * item.quantity).toFixed(2)}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OrderHistory;