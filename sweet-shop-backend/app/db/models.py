from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship 
from .database import Base

# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True) # Corrected syntax to use default=True
    
    # Relationship for all the sweets this user/admin manages
    sweets = relationship("Sweet", back_populates="owner")
    
# --- Sweet Model (Corrected) ---   
class Sweet(Base):
    __tablename__ = "sweets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True) # Added length for String
    description = Column(String(500), nullable=True)  
    category = Column(String(50), index=True) # Added length for String
    price = Column(Float)
    stock_quantity = Column(Integer, default=0) 
    
    # Added is_available to match Pydantic schema
    is_available = Column(Boolean, default=True)

    # Link to the User/Admin who manages this sweet
    owner_id = Column(Integer, ForeignKey("users.id")) 
    
    # Relationship back to the User model
    owner = relationship("User", back_populates="sweets")