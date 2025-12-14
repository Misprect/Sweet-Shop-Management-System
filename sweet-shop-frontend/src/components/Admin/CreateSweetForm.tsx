// src/components/Admin/CreateSweetForm.tsx (FINALIZED CODE)

import React, { useState } from 'react';
import api from '../../api/index.ts';
import { Sweet } from '../../types/Sweet.ts';

// Add the interface for the props
interface CreateSweetFormProps {
    onSweetCreated: () => void; // Function passed from Dashboard to refresh the list
}

const CreateSweetForm: React.FC<CreateSweetFormProps> = ({ onSweetCreated }) => {
    // State Declarations
    const [name, setName] = useState('');
    const [price, setPrice] = useState(''); // Holds the string input value
    const [description, setDescription] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccessMessage(null);
        setLoading(true);

        // 1. Basic validation and conversion (defines sweetPrice)
        const sweetPrice = parseFloat(price);
        if (isNaN(sweetPrice) || sweetPrice <= 0) {
            setError('Please enter a valid price greater than zero.');
            setLoading(false);
            return;
        }

        try {
            // 2. CONSTRUCT sweetData WITH BACKEND REQUIRED FIELDS
            const sweetData = {
                name,
                price: sweetPrice, 
                description,
                
                // --- REQUIRED DEFAULT VALUES ADDED HERE TO RESOLVE 422 ERROR ---
                stock_quantity: 100, 
                is_available: true,
                category: 'General', 
                // -----------------------------------------------------------------
            };

            // Call the new backend endpoint: POST /api/sweets/
            const response = await api.post<Sweet>('/sweets/', sweetData);
            
            setSuccessMessage(`Sweet "${response.data.name}" added successfully!`);
            
            // Clear the form fields after successful creation
            setName('');
            setPrice('');
            setDescription('');

            // Call the refresh function to update the dashboard
            onSweetCreated(); 

        } catch (err: any) {
            let errorMessage = 'An unexpected error occurred during creation.';
            if (err.response && err.response.data && err.response.data.detail) {
                 if (typeof err.response.data.detail === 'string') {
                    errorMessage = err.response.data.detail;
                } else if (Array.isArray(err.response.data.detail)) {
                    // This handles validation errors that return a list of error objects
                    errorMessage = err.response.data.detail
                        .map((d: any) => `${d.loc.slice(-1)[0]}: ${d.msg}`)
                        .join('; ');
                }
            } else if (err.message) {
                 errorMessage = err.message;
            }
            
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // JSX Content (Form structure remains correct)
    return (
        <div className="card shadow mb-4">
            <div className="card-header bg-primary text-white">
                <h5 className="mb-0">Add New Sweet to Inventory</h5>
            </div>
            <div className="card-body">
                {/* Display Error and Success Messages */}
                {error && <div className="alert alert-danger">{error}</div>}
                {successMessage && <div className="alert alert-success">{successMessage}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="sweetName" className="form-label">Sweet Name</label>
                        <input
                            type="text"
                            className="form-control"
                            id="sweetName"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label htmlFor="sweetPrice" className="form-label">Price (₹)</label>
                        <input
                            type="number"
                            className="form-control"
                            id="sweetPrice"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            step="0.01"
                            min="0.01"
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label htmlFor="sweetDescription" className="form-label">Description</label>
                        <textarea
                            className="form-control"
                            id="sweetDescription"
                            rows={3}
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Adding...' : 'Create Sweet'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateSweetForm;