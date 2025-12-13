from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- Order Item Schemas ---

class OrderItemBase(BaseModel):
    """Base schema for an item within an order."""
    sweet_id: int = Field(..., description="The ID of the sweet product being ordered.")
    quantity: int = Field(..., gt=0, description="The quantity of the sweet being ordered.")


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item. Used within OrderCreate."""
    pass


class OrderItem(OrderItemBase):
    """Schema for reading (returning) an existing order item."""
    id: int
    order_id: int
    price_at_purchase: float
    
    # We could embed the full Sweet schema here, but for simplicity, we'll keep it concise for now.
    
    model_config = ConfigDict(from_attributes=True)


# --- Order Schemas ---

class OrderBase(BaseModel):
    """Base schema for an order."""
    # Note: total_price and status are not included here because they are calculated/defaulted by the backend
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
    
    # Embeds the OrderItem schema to show what's in the order
    items: List[OrderItem] = []
    
    model_config = ConfigDict(from_attributes=True)