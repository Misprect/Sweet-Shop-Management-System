// src/components/Admin/SweetListAdmin.tsx

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/index.ts';
import useAuth from '../../hooks/useAuth.ts';

// Re-using the Sweet structure
interface Sweet {
    id: number;
    name: string;
    description: string;
    category: string;
    price: number;
    stock_quantity: number;
    is_available: boolean;
}

const SweetListAdmin: React.FC = () => {
    const { user } = useAuth();
    const [sweets, setSweets] = useState<Sweet[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    // Fetch the list of all sweets
    const fetchSweets = async () => {
        setLoading(true);
        try {
            // Note: Assuming /sweets/ endpoint returns all sweets regardless of is_available for Admin
            const response = await api.get<Sweet[]>('/sweets/');
            setSweets(response.data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch sweets for admin:', err);
            setError('Failed to load sweets inventory. Check backend connection.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Ensure only admin fetches this data (AdminRoute should handle this, but it's a good safety check)
        if (user?.is_admin) {
            fetchSweets();
        }
    }, [user]);

    // Function to handle deletion of a sweet
    const handleDelete = async (sweetId: number) => {
        if (!window.confirm("Are you sure you want to delete this sweet?")) {
            return;
        }

        try {
            // Assuming the delete endpoint is /sweets/{id}
            await api.delete(`/sweets/${sweetId}`);
            // Refresh the list after successful deletion
            fetchSweets(); 
            alert('Sweet deleted successfully.');
        } catch (err) {
            console.error('Deletion failed:', err);
            alert('Failed to delete sweet. Check permissions or network.');
        }
    };

    if (loading) {
        return <div className="text-center mt-5">Loading sweet inventory...</div>;
    }

    if (error) {
        return <div className="alert alert-danger mt-5 text-center">{error}</div>;
    }
    
    // Safety check (AdminRoute handles this, but good practice)
    if (!user || !user.is_admin) {
         return <div className="alert alert-danger mt-5 text-center">Unauthorized Access.</div>;
    }


    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="mb-0">Admin Sweet Inventory Management</h2>
                {/* Link to the SweetForm component for creation */}
                <Link to="/admin/sweets/new" className="btn btn-primary">
                    + Add New Sweet
                </Link>
            </div>
            
            {sweets.length === 0 ? (
                <div className="alert alert-info text-center">
                    No sweets found in the system. Click 'Add New Sweet' to start.
                </div>
            ) : (
                <table className="table table-striped table-hover shadow-sm">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Price</th>
                            <th>Stock</th>
                            <th>Available</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sweets.map((sweet) => (
                            <tr key={sweet.id}>
                                <td>{sweet.id}</td>
                                <td>{sweet.name}</td>
                                <td>{sweet.category}</td>
                                <td>₹{sweet.price.toFixed(2)}</td>
                                <td>{sweet.stock_quantity}</td>
                                <td>
                                    <span className={`badge ${sweet.is_available ? 'bg-success' : 'bg-danger'}`}>
                                        {sweet.is_available ? 'Yes' : 'No'}
                                    </span>
                                </td>
                                <td>
                                    {/* Link to the SweetForm for editing */}
                                    <Link 
                                        to={`/admin/sweets/edit/${sweet.id}`} 
                                        className="btn btn-sm btn-warning me-2"
                                    >
                                        Edit
                                    </Link>
                                    <button 
                                        className="btn btn-sm btn-danger"
                                        onClick={() => handleDelete(sweet.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default SweetListAdmin;