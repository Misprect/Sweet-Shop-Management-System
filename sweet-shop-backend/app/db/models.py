from sqlalchemy import Column, Integer, String, Boolean, Float
from .database import Base

# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean(name='is_active'), default=True) # Explicit boolean name for compatibility
    
# --- Sweet Model ---
class Sweet(Base):
    __tablename__ = "sweets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer, default=0)