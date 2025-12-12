from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone # Updated timezone import
from typing import Optional
from jose import jwt, JWTError # Added JWTError
from sqlalchemy.orm import Session # Required for database interaction

# NEW IMPORTS FOR AUTH DEPENDENCIES
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# End of new imports

from .config import settings
# Import your database and model dependencies (these should exist in your project structure)
from ..db.database import get_db
# Use local import for User model to avoid circular dependency issues during testing
# from ..db.models import User # If you need a global import

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 1. Password Hashing/Verification ---

def get_password_hash(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

# --- 2. Token Creation ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        # Use timezone.utc for full compatibility with datetime.now(timezone.utc)
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # NOTE: Changed datetime.utcnow() to datetime.now(timezone.utc) + timedelta
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Note: Use "sub" (subject) for the user identifier (email) in the token payload
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- 3. Token Validation and User Retrieval (The Missing Code) ---

# This defines the FastAPI dependency that looks for the 'Authorization: Bearer <token>' header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_user_by_email(db: Session, email: str):
    """Utility function to retrieve a user by email."""
    # Local import is safer here if models is involved in main.py initialization
    from app.db.models import User 
    return db.query(User).filter(User.email == email).first()

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Retrieves the user associated with the access token by decoding the JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: get_current_user = Depends(get_current_user)):
    """The function that was missing! Ensures the user retrieved by the token is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user