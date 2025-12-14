// src/components/Admin/OrderListAdmin.tsx

import React, { useState, useEffect } from 'react';
import api from '../../api/index.ts'; 
import useAuth from '../../hooks/useAuth.ts';

// --- Type Definitions ---
interface OrderItem {
    name: string;
    quantity: number;
    price_at_purchase: number;
}

interface Order {
    id: number;
    user_id: number;
    user_email: string; // Assuming the backend joins user data
    order_date: string;
    total_amount: number;
    status: 'pending' | 'processing' | 'completed' | 'cancelled';
    items: OrderItem[];
}

// Order Status options for the dropdown
const statusOptions = ['pending', 'processing', 'completed', 'cancelled'];

const OrderListAdmin: React.FC = () => {
    const { user } = useAuth();
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchOrders = async () => {
        setLoading(true);
        try {
            // Assuming Admin has access to a dedicated /orders/ endpoint
            const response = await api.get<Order[]>('/orders/'); 
            setOrders(response.data.reverse()); // Show newest orders first
            setError(null);
        } catch (err) {
            console.error('Failed to fetch orders:', err);
            setError('Failed to load orders. Check the backend endpoint /orders/.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user?.is_admin) {
            fetchOrders();
        }
    }, [user]);

    // Handle changing the status of an order
    const handleStatusChange = async (orderId: number, newStatus: string) => {
        if (!window.confirm(`Are you sure you want to change Order #${orderId} status to "${newStatus}"?`)) {
            return;
        }

        try {
            // Assuming a PUT/PATCH endpoint like /orders/{id}/status
            await api.patch(`/orders/${orderId}/status`, { status: newStatus });
            
            // Update the local state instead of refetching everything (more efficient)
            setOrders(prevOrders => prevOrders.map(order => 
                order.id === orderId ? { ...order, status: newStatus as Order['status'] } : order
            ));
            alert(`Order #${orderId} status updated to ${newStatus}.`);

        } catch (err) {
            console.error('Status update failed:', err);
            alert('Failed to update order status.');
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
            <h2 className="mb-4">Customer Order Management</h2>
            
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
                                        ${order.status === 'completed' ? 'bg-success' : 
                                          order.status === 'processing' ? 'bg-warning text-dark' : 
                                          order.status === 'cancelled' ? 'bg-danger' : 
                                          'bg-primary'}`}>
                                        {order.status}
                                    </span>
                                </div>
                                <div className="card-body">
                                    <p className="mb-1"><strong>Customer:</strong> {order.user_email || `User ID: ${order.user_id}`}</p>
                                    <p className="mb-1"><strong>Order Date:</strong> {new Date(order.order_date).toLocaleDateString()}</p>
                                    <p className="h4 text-success mb-3"><strong>Total:</strong> ₹{order.total_amount.toFixed(2)}</p>
                                    
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
                                            disabled={loading} // Prevent multiple clicks
                                        >
                                            {statusOptions.map(status => (
                                                <option key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>
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