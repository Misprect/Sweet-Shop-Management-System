from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone 
from typing import Optional
from jose import jwt, JWTError 
from sqlalchemy.orm import Session 

# REQUIRED IMPORTS FOR AUTH DEPENDENCIES
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# End of new imports

from .config import settings
# Import your database and model dependencies (these should exist in your project structure)
from ..db.database import get_db
# Note: Since the User model is imported locally in get_user_by_email, 
# we don't need a top-level import here, which helps avoid circular imports.
# from ..db.models import User # (Keep this commented out)

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
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- 3. Token Validation and User Retrieval ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_user_by_email(db: Session, email: str):
    """Utility function to retrieve a user by email."""
    # Local import is safer here to prevent issues with module loading order
    from app.db.models import User as UserModel # <-- Use an alias for clarity
    return db.query(UserModel).filter(UserModel.email == email).first()

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
    """Ensures the user retrieved by the token is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- 4. NEW FUNCTION TO RESOLVE THE IMPORT ERROR ---

def get_current_admin_user(current_user: get_current_user = Depends(get_current_active_user)):
    """
    Dependency that verifies the token, finds the active user, 
    and checks if the user has admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted: Admin privileges required."
        )
    return current_user