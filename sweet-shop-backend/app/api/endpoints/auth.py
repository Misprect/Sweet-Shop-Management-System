from fastapi import APIRouter, Depends, HTTPException, status
# REQUIRED FOR THE LOGIN ENDPOINT
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from datetime import timedelta

# Import your dependencies
from ...db.database import get_db
from ...db.models import User as UserModel
from ...schemas.user import UserCreate, Token
from ...core.security import (
    get_password_hash, 
    create_access_token,
    verify_password  # Used in the login endpoint
)
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- 1. POST /auth/register ---
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Handles user registration and returns a JWT."""
    
    # Check for existing user
    db_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_in.password)
    
    # Logic: First user created is automatically an admin
    is_admin = not db.query(UserModel).first()
    
    db_user = UserModel(email=user_in.email, hashed_password=hashed_password, is_admin=is_admin, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "is_admin": is_admin},
        expires_delta=access_token_expires
    )
    
    role = "admin" if is_admin else "user"
    # Note: Returning user_role is highly recommended for client-side use
    return {"access_token": access_token, "token_type": "bearer", "user_role": role}


# --- 2. POST /auth/token (THE MISSING LOGIN ENDPOINT) ---
@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Handles user login using OAuth2 form data (username/password)."""
    
    # 1. Find the user by username (which is email)
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    # 2. Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create the token
    is_admin = user.is_admin
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "is_admin": is_admin},
        expires_delta=access_token_expires
    )
    
    role = "admin" if is_admin else "user"
    return {"access_token": access_token, "token_type": "bearer", "user_role": role}