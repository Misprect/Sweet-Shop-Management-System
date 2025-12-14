from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from fastapi import APIRouter

router = APIRouter(
    prefix="/user", 
    tags=["Users"]
)

# --- Input Schemas ---

# Schema for user registration (Input)
class UserCreate(BaseModel):
    """Schema for a new user registration."""
    email: EmailStr  # Use EmailStr for better validation
    password: str = Field(..., min_length=8)

# Schema for user login/credentials (Input)
class UserLogin(BaseModel):
    """Schema for user authentication credentials."""
    email: EmailStr
    password: str

# --- Base/Core Schemas ---
class UserBase(BaseModel):
    """Base schema containing common user fields."""
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True

    # Pydantic setting to allow mapping from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)


# --- Output Schemas (for API responses) ---
class User(UserBase):
    """Schema for returning user data (used internally/for owners)."""
    id: int

class UserOut(User):
    """Schema for public user output (excludes sensitive info like hashed_password)."""
    pass

# --- Token Schemas ---

# Schema for the JWT token response (Output)
class Token(BaseModel):
    """Schema for the JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_role: str # Added role for easy client-side authorization checks

# Schema for decoding and verifying token payload
class TokenData(BaseModel):
    """Schema for decoding and verifying token payload."""
    user_id: Optional[int] = None