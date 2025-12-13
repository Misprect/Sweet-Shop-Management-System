from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text 
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from datetime import datetime, UTC # <-- CORRECTED: Added UTC for timezone-aware operation
from .database import Base

# --- User Model (Updated) ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True) 
    
    # Relationship for all the sweets this user/admin manages
    sweets = relationship("Sweet", back_populates="owner")
    
    # NEW: Relationship for all orders placed by this user
    orders = relationship("Order", back_populates="owner") 
    
# --- Sweet Model (Updated) ---  
class Sweet(Base):
    __tablename__ = "sweets"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(100), unique=True, index=True) 
    description = Column(Text, nullable=True) 
    category = Column(String(50), index=True)
    price = Column(Float)
    stock_quantity = Column(Integer, default=0) 
    is_available = Column(Boolean, default=True)

    # Link to the User/Admin who manages this sweet
    owner_id = Column(Integer, ForeignKey("users.id")) 
    
    # Relationship back to the User model
    owner = relationship("User", back_populates="sweets")
    
    # NEW: Relationship to track which order items reference this sweet
    order_items = relationship("OrderItem", back_populates="sweet")

# --- NEW: Order Model ---
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    
    # Status of the order (e.g., "Pending", "Processing", "Delivered", "Canceled")
    status = Column(String, default="Pending", nullable=False)
    
    # Total price of the order at the time of purchase
    total_price = Column(Float, nullable=False)
    
    # Timestamps
    # FIX APPLIED: Changed datetime.utcnow to datetime.now(UTC)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Foreign Key to link to the User who placed the order
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# --- NEW: OrderItem Model ---
# This table stores the specific sweets, quantity, and the price at the time of purchase.
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key to link to the specific order
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Foreign Key to link to the sweet product being ordered
    sweet_id = Column(Integer, ForeignKey("sweets.id"), nullable=False)
    
    # Data captured at the time of purchase
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False) 
    
    # Relationships
    order = relationship("Order", back_populates="items")
    sweet = relationship("Sweet", back_populates="order_items")