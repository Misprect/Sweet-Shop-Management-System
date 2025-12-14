from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- 1. Order Item Schemas ---

class OrderItemBase(BaseModel):
    """Base schema for an item within an order."""
    sweet_id: int = Field(..., description="The ID of the sweet product being ordered.")
    quantity: int = Field(..., gt=0, description="The quantity of the sweet being ordered.")
    
    # *** CRITICAL FIX: ADDING THE NAME FIELD FOR RESPONSES ***
    name: Optional[str] = Field(None, description="The name of the sweet product.")


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item. Used within OrderCreate."""
    # The client does not send the name, so we must exclude it from the request body validation
    name: Optional[str] = Field(None, exclude=True)
    pass


class OrderItem(OrderItemBase):
    """Schema for reading (returning) an existing order item."""
    id: int
    order_id: int
    price_at_purchase: float
    # The 'name' field is inherited from OrderItemBase and will be populated by the backend query/mapping.
    
    model_config = ConfigDict(from_attributes=True)


# --- 2. Order Schemas ---

class OrderBase(BaseModel):
    """Base schema for an order."""
    pass


class OrderCreate(OrderBase):
    """Schema for receiving order creation data from the client."""
    items: List[OrderItemCreate] = Field(..., description="A list of items and quantities for the order.")


class Order(OrderBase):
    """Schema for reading (returning) a full existing order."""
    id: int
    owner_id: int
    status: str
    total_price: float
    created_at: datetime
    updated_at: datetime
    
    # Embeds the OrderItem schema to show what's in the order (now includes 'name')
    items: List[OrderItem] = []
    
    model_config = ConfigDict(from_attributes=True)


# --- 3. NEW Admin and Status Schemas (ADDED) ---

class OrderStatusUpdate(BaseModel):
    """Schema for receiving status update data from the client (Admin PATCH)."""
    status: str = Field(..., description="The new status for the order (e.g., Pending, Shipped, Delivered).")


class OrderAdmin(Order):
    """
    Schema for reading a full existing order, including the associated user's email.
    Used exclusively for Admin views (GET /orders/).
    """
    # This field is populated by the join in the SQL query when an admin fetches all orders
    user_email: Optional[str] = Field(None, description="The email address of the user who placed the order.")
    
    # Inherits all other fields (id, owner_id, total_price, items, etc.) from the base Order schema
    
    model_config = ConfigDict(from_attributes=True)