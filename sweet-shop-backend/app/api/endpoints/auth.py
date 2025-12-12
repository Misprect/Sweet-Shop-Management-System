from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ...db.database import get_db
from ...db.models import User as UserModel
from ...schemas.user import UserCreate, Token
from ...core.security import get_password_hash, create_access_token
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Handles user registration and returns a JWT."""
    
    # 1. Check for existing user (Satisfies the failure test)
    db_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash password and create user
    hashed_password = get_password_hash(user_in.password)
    
    # Logic: First user created is automatically an admin
    is_admin = not db.query(UserModel).first()
    
    db_user = UserModel(email=user_in.email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 3. Generate token (Satisfies the success assertions)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "is_admin": is_admin},
        expires_delta=access_token_expires
    )
    
    role = "admin" if is_admin else "user"
    return {"access_token": access_token, "token_type": "bearer", "user_role": role}