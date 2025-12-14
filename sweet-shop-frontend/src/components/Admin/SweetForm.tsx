// src/components/Admin/SweetForm.tsx

import React, { useState, useEffect } from 'react';
import api from '../../api/index.ts';
import { useNavigate, useParams } from 'react-router-dom'; // IMPORTED: useParams
import useAuth from '../../hooks/useAuth.ts';

// Define the structure for the sweet data sent to the form and API
interface SweetFormData {
    name: string;
    description: string;
    category: string;
    price: string; 
    stock_quantity: string;
    is_available: boolean;
}

// Define the full Sweet structure for fetching existing data
interface Sweet {
    id: number;
    name: string;
    description: string;
    category: string;
    price: number;
    stock_quantity: number;
    is_available: boolean;
}

const SweetForm: React.FC = () => {
    // Get the 'id' parameter from the URL (will be undefined if creating a new sweet)
    const { id } = useParams<{ id?: string }>(); 
    const isEditMode = !!id; // Boolean flag to track if we are editing
    
    const { user } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState<SweetFormData>({
        name: '',
        description: '',
        category: '',
        price: '0.00',
        stock_quantity: '0',
        is_available: true,
    });
    
    const [loading, setLoading] = useState(false);
    const [fetchLoading, setFetchLoading] = useState(isEditMode); // Loading state for fetching existing data
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // --- 1. Fetch existing data for Edit Mode ---
    useEffect(() => {
        if (!isEditMode) return;
        
        const fetchSweetData = async () => {
            try {
                const response = await api.get<Sweet>(`/sweets/${id}`);
                const sweet = response.data;
                
                // Populate the form state with fetched data
                setFormData({
                    name: sweet.name,
                    description: sweet.description,
                    category: sweet.category,
                    // Convert numbers back to strings for form inputs
                    price: sweet.price.toFixed(2), 
                    stock_quantity: String(sweet.stock_quantity),
                    is_available: sweet.is_available,
                });
            } catch (err) {
                console.error('Failed to fetch sweet for editing:', err);
                setError('Failed to load sweet details. It might not exist.');
            } finally {
                setFetchLoading(false);
            }
        };
        
        fetchSweetData();
    }, [id, isEditMode]); // Dependency array includes id and edit mode flag

    // Handles input changes
    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    // Handles checkbox changes
    const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, checked } = e.target;
        setFormData(prev => ({ ...prev, [name]: checked }));
    };

    // --- 2. Handle Submission (POST for Create, PUT for Edit) ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        const payload = {
            ...formData,
            price: parseFloat(formData.price),
            stock_quantity: parseInt(formData.stock_quantity, 10),
        };
        
        try {
            if (isEditMode) {
                // EDIT LOGIC: Send PUT request to update existing sweet
                await api.put(`/sweets/${id}`, payload);
                setSuccess('Sweet updated successfully!');
            } else {
                // CREATE LOGIC: Send POST request for new sweet
                await api.post('/sweets/', payload);
                setSuccess('Sweet added successfully!');
                
                // Clear form for creation mode
                setFormData({ name: '', description: '', category: '', price: '0.00', stock_quantity: '0', is_available: true });
            }

            // After success, navigate back to the admin list
            setTimeout(() => navigate('/admin/sweets'), 1500); 

        } catch (err: any) {
            console.error('Sweet operation failed:', err);
            const errorMessage = err.response?.data?.detail || 'Failed to save sweet. Check inputs.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    
    if (!user || !user.is_admin) {
        return <div className="alert alert-danger mt-5 text-center">Unauthorized Access.</div>;
    }
    
    // Show loading spinner while fetching data in Edit Mode
    if (fetchLoading) {
        return <div className="text-center mt-5">Loading sweet data for editing...</div>;
    }


    return (
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-lg-8">
                    <div className="card shadow-lg">
                        <div className="card-header bg-success text-white">
                            <h3 className="mb-0">
                                {isEditMode ? `Edit Sweet (ID: ${id})` : 'Add New Sweet'}
                            </h3>
                        </div>
                        <div className="card-body">
                            {/* Status Messages */}
                            {error && <div className="alert alert-danger">{error}</div>}
                            {success && <div className="alert alert-success">{success}</div>}

                            <form onSubmit={handleSubmit}>
                                {/* Form fields remain the same */}
                                <div className="mb-3">
                                    <label htmlFor="name" className="form-label">Name</label>
                                    <input type="text" className="form-control" id="name" name="name" value={formData.name} onChange={handleChange} required />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="category" className="form-label">Category</label>
                                    <input type="text" className="form-control" id="category" name="category" value={formData.category} onChange={handleChange} required />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="description" className="form-label">Description</label>
                                    <textarea className="form-control" id="description" name="description" rows={3} value={formData.description} onChange={handleChange} required />
                                </div>

                                {/* Price and Stock (Inline) */}
                                <div className="row">
                                    <div className="col-md-6 mb-3">
                                        <label htmlFor="price" className="form-label">Price (₹)</label>
                                        <input type="number" className="form-control" id="price" name="price" value={formData.price} onChange={handleChange} step="0.01" min="0.01" required />
                                    </div>
                                    <div className="col-md-6 mb-3">
                                        <label htmlFor="stock_quantity" className="form-label">Stock Quantity</label>
                                        <input type="number" className="form-control" id="stock_quantity" name="stock_quantity" value={formData.stock_quantity} onChange={handleChange} min="0" required />
                                    </div>
                                </div>

                                {/* Is Available Checkbox */}
                                <div className="form-check mb-4">
                                    <input className="form-check-input" type="checkbox" id="is_available" name="is_available" checked={formData.is_available} onChange={handleCheckboxChange} />
                                    <label className="form-check-label" htmlFor="is_available">
                                        Available for Sale
                                    </label>
                                </div>

                                {/* Submit Button */}
                                <button type="submit" className="btn btn-success w-100" disabled={loading}>
                                    {loading ? 'Saving...' : isEditMode ? 'Update Sweet' : 'Add Sweet'}
                                </button>
                                
                                <Link to="/admin/sweets" className="btn btn-outline-secondary w-100 mt-2">
                                    Back to Sweet List
                                </Link>
                                
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SweetForm;