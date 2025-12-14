// src/components/SweetCard.tsx

import React from 'react';
// Note: Interfaces are defined here or should be imported from Dashboard.tsx if used elsewhere
// Since this file is self-contained, we define them here for clarity.

// --- Type Definitions ---
interface Sweet {
    id: number;
    name: string;
    description: string;
    category: string;    
    price: number;
    stock_quantity: number;
    is_available: boolean; // Indicates if the admin marked it for sale
}

interface SweetCardProps {
    sweet: Sweet;
    addToCart: (sweet: Sweet) => void; 
}

const SweetCard: React.FC<SweetCardProps> = ({ sweet, addToCart }) => {
    
    // A sweet is available if stock > 0 AND the admin marked it as available
    const isAvailable = sweet.stock_quantity > 0 && sweet.is_available;
    const stockStatusClass = isAvailable ? 'text-success' : 'text-danger';

    return (
        <div className="col">
            <div className={`card h-100 shadow-sm ${!isAvailable ? 'bg-light-subtle' : ''}`}>
                <div className="card-body d-flex flex-column">
                    <h5 className="card-title text-primary">{sweet.name}</h5>
                    <p className="card-text text-muted small">{sweet.description}</p>
                    
                    <div className="mt-auto pt-2">
                        <p className="mb-1">
                            {/* Display price in rupees */}
                            <strong>Price:</strong> <span className="text-success fw-bold">₹{sweet.price.toFixed(2)}</span>
                        </p>
                        <p className="mb-3">
                            <strong>Stock:</strong> 
                            <span className={`fw-bold ms-2 ${stockStatusClass}`}>
                                {isAvailable ? `${sweet.stock_quantity} available` : 'Out of Stock'}
                            </span>
                        </p>

                        <button 
                            className="btn btn-sm btn-primary w-100"
                            onClick={() => addToCart(sweet)}
                            disabled={!isAvailable} 
                        >
                            {isAvailable ? 'Add to Cart' : 'Unavailable'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SweetCard;