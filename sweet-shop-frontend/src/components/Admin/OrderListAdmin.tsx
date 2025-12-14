// src/components/Admin/OrderListAdmin.tsx (FINAL DISPLAY FIX)

import React, { useState, useEffect } from 'react';
import api from '../../api/index.ts'; 
import useAuth from '../../hooks/useAuth.ts';
// Assuming the Order and OrderItem types are still used for standard structure
import { Order as UserOrder, OrderItem as UserOrderItem } from '../../types/Order.ts'; 

// --- Type Definitions for Admin View ---
// These types must match the Pydantic OrderAdmin schema from the backend
interface AdminOrderItem {
    sweet_id: number;
    name: string; // Assuming the backend now includes the name in the admin response
    quantity: number;
    price_at_purchase: float;
}

interface AdminOrder {
    id: number;
    owner_id: number;
    user_email?: string; // CRITICAL: This field is now included for admins (may be optional)
    created_at: string; 
    total_price: number; 
    status: 'Pending' | 'Processing' | 'Shipped' | 'Delivered' | 'Cancelled'; 
    items: AdminOrderItem[];
}

// Order Status options for the dropdown
const statusOptions = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'];

// --- Component Definition ---

const OrderListAdmin: React.FC = () => {
    const { user } = useAuth() as { user: { is_admin: boolean } | null }; 
    
    const [orders, setOrders] = useState<AdminOrder[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // NEW HELPER FUNCTION TO FORMAT DISPLAY NAME
    const getDisplayName = (email: string | undefined, ownerId: number): string => {
        if (email) {
            // 1. Get the local part (before '@')
            const localPart = email.split('@')[0];
            
            // 2. Take the first 4 characters
            const shortName = localPart.substring(0, Math.min(localPart.length, 4));
            
            // 3. Capitalize the first letter of the short name
            const capitalizedShortName = shortName.charAt(0).toUpperCase() + shortName.slice(1);
            
            // 4. Return the desired format
            return `${capitalizedShortName} (${email})`;
        }
        return `User ID: ${ownerId}`;
    };
    // END NEW HELPER FUNCTION

    const fetchOrders = async () => {
        setLoading(true);
        try {
            // This endpoint should now return the user_email field for admins
            const response = await api.get<AdminOrder[]>('/orders/'); 
            
            // Assuming the list of orders is directly in response.data
            setOrders(response.data.reverse()); 
            setError(null);
        } catch (err: any) {
            console.error('Failed to fetch orders:', err);
            const errorMessage = err.response?.data?.detail || 'Failed to load orders. Check the admin endpoint.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user?.is_admin) {
            fetchOrders();
        }
    }, [user]);

    const handleStatusChange = async (orderId: number, newStatus: string) => {
        if (!window.confirm(`Are you sure you want to change Order #${orderId} status to "${newStatus}"?`)) {
            return;
        }

        try {
            // Using the fixed PATCH endpoint /orders/{id}/status
            await api.patch(`/orders/${orderId}/status`, { status: newStatus });
            
            setOrders(prevOrders => prevOrders.map(order => 
                order.id === orderId ? { ...order, status: newStatus as AdminOrder['status'] } : order
            ));
            alert(`Order #${orderId} status updated to ${newStatus}.`);

        } catch (err: any) {
            console.error('Status update failed:', err);
            const errorMessage = err.response?.data?.detail || 'Failed to update order status.';
            alert(errorMessage);
        }
    };
    
    if (!user || !user.is_admin) {
        return <div className="alert alert-danger mt-5 text-center">Unauthorized Access.</div>;
    }

    if (loading) {
        return <div className="text-center mt-5">Loading customer orders...</div>;
    }

    if (error) {
        return <div className="alert alert-danger mt-5 text-center">{error}</div>;
    }

    return (
        <div className="container mt-4">
            <h2 className="mb-4">📋 Customer Order Management</h2>
            
            {orders.length === 0 ? (
                <div className="alert alert-info text-center">
                    No customer orders have been placed yet.
                </div>
            ) : (
                <div className="row g-4">
                    {orders.map((order) => (
                        <div className="col-lg-6" key={order.id}>
                            <div className="card shadow-sm h-100">
                                <div className="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                                    <h5 className="mb-0">Order ID: #{order.id}</h5>
                                    <span className={`badge text-capitalize 
                                        ${order.status === 'Delivered' ? 'bg-success' : 
                                            order.status === 'Processing' ? 'bg-warning text-dark' : 
                                            order.status === 'Cancelled' ? 'bg-danger' : 
                                            'bg-primary'}`}>
                                        {order.status}
                                    </span>
                                </div>
                                <div className="card-body">
                                    {/* FIX APPLIED HERE: Using the new helper function */}
                                    <p className="mb-1">
                                        <strong>Customer:</strong> {getDisplayName(order.user_email, order.owner_id)}
                                    </p>
                                    <p className="mb-1"><strong>Order Date:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
                                    <p className="h4 text-success mb-3"><strong>Total:</strong> ₹{order.total_price.toFixed(2)}</p>
                                    
                                    <h6 className="mt-3">Items Purchased:</h6>
                                    <ul className="list-group list-group-flush small mb-3">
                                        {order.items.map((item, index) => (
                                            <li key={index} className="list-group-item d-flex justify-content-between">
                                                <span>{item.name}</span>
                                                <span className="fw-bold">{item.quantity} units</span>
                                                <span className="text-muted">₹{(item.price_at_purchase * item.quantity).toFixed(2)}</span>
                                            </li>
                                        ))}
                                    </ul>
                                    
                                    {/* Status Update Control */}
                                    <div className="d-flex align-items-center mt-3">
                                        <label htmlFor={`status-${order.id}`} className="form-label me-2 mb-0 fw-bold">Update Status:</label>
                                        <select
                                            id={`status-${order.id}`}
                                            className="form-select form-select-sm"
                                            value={order.status}
                                            onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                            disabled={loading} 
                                        >
                                            {statusOptions.map(status => (
                                                <option key={status} value={status}>{status}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OrderListAdmin;