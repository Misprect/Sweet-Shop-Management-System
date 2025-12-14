// src/components/CartSummary.tsx
import React from 'react';

// --- Type Definitions ---
// Note: It's best practice to define this type in a central file (like Dashboard.tsx) 
// and import it, but we define it here for completeness.
interface CartItem {
    sweet_id: number;
    name: string;
    price_at_purchase: number;
    quantity: number;
}

interface CartSummaryProps {
    cart: CartItem[];
    setCart: React.Dispatch<React.SetStateAction<CartItem[]>>;
    // CRITICAL FIX: Ensure placeOrder is typed as a Promise<void> since it's an async function
    placeOrder: () => Promise<void>; 
}

const CartSummary: React.FC<CartSummaryProps> = ({ cart, setCart, placeOrder }) => {

    const calculateTotal = () => {
        return cart.reduce((total, item) => total + (item.price_at_purchase * item.quantity), 0);
    };

    /**
     * Updates the quantity of a sweet in the cart.
     * If the new quantity is 0 or less, the item is removed from the cart.
     */
    const updateQuantity = (sweetId: number, delta: number) => {
        setCart(prevCart => {
            return prevCart
                .map(item => 
                    item.sweet_id === sweetId 
                        ? { ...item, quantity: item.quantity + delta } 
                        : item
                )
                .filter(item => item.quantity > 0); // Removes items where quantity drops to 0 or less
        });
    };
    
    // Function to completely remove an item (alternative to using updateQuantity with a large negative delta)
    const removeItem = (sweetId: number) => {
        setCart(prevCart => prevCart.filter(item => item.sweet_id !== sweetId));
    };

    const total = calculateTotal();

    return (
        <div className="card shadow-sm sticky-top" style={{ top: '6rem' }}>
            <div className="card-header bg-primary text-white">
                <h4 className="mb-0">🛒 Your Cart</h4>
            </div>
            <div className="card-body">
                {cart.length === 0 ? (
                    <p className="text-center text-muted">Cart is empty. Add some delicious sweets!</p>
                ) : (
                    <ul className="list-group list-group-flush">
                        {cart.map(item => (
                            <li 
                                key={item.sweet_id} 
                                className="list-group-item d-flex justify-content-between align-items-center"
                            >
                                <div>
                                    <span className="fw-bold">{item.name}</span>
                                    <div className="text-muted small">
                                        ₹{item.price_at_purchase.toFixed(2)}
                                    </div>
                                </div>
                                <div className="d-flex align-items-center">
                                    {/* Decrement Button */}
                                    <button 
                                        className="btn btn-sm btn-outline-secondary me-2"
                                        // Decrease quantity (or remove item if it reaches 0)
                                        onClick={() => updateQuantity(item.sweet_id, -1)}
                                        disabled={item.quantity <= 1} // Disables if quantity is 1 (to force use of the remove button)
                                    >
                                        -
                                    </button>
                                    <span className="fw-bold me-2">
                                        {item.quantity}
                                    </span>
                                    {/* Increment Button */}
                                    <button 
                                        className="btn btn-sm btn-outline-secondary"
                                        onClick={() => updateQuantity(item.sweet_id, 1)}
                                    >
                                        +
                                    </button>
                                </div>
                                {/* Item Total & Remove */}
                                <div className="text-end">
                                    <span className="fw-bold d-block text-primary">
                                        ₹{(item.price_at_purchase * item.quantity).toFixed(2)}
                                    </span>
                                    <button
                                        className="btn btn-sm btn-link p-0 text-danger"
                                        onClick={() => removeItem(item.sweet_id)}
                                    >
                                        Remove
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
            
            <div className="card-footer">
                <div className="d-flex justify-content-between fw-bold mb-3">
                    <span>Total:</span>
                    <span className="text-success">₹{total.toFixed(2)}</span>
                </div>
                <button 
                    className="btn btn-lg btn-success w-100"
                    onClick={placeOrder}
                    disabled={cart.length === 0}
                >
                    Place Order
                </button>
                <button 
                    className="btn btn-sm btn-link text-danger w-100 mt-2"
                    onClick={() => setCart([])}
                    disabled={cart.length === 0}
                >
                    Clear Cart
                </button>
            </div>
        </div>
    );
};

export default CartSummary;