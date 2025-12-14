from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import your dependencies
from ...db.database import get_db
from ...db.models import User as UserModel
from ...schemas.user import UserOut # Import UserOut schema from the schemas folder
from ...core.security import get_current_active_user, get_current_admin_user 

# --- Router Definition ---
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# --- 1. GET /users/me (Get Current User Profile) ---
@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """Returns the profile of the currently logged-in active user."""
    return current_user

# --- 2. GET /users/ (Admin only) ---
# This endpoint handles the root path and resolves the 404 error
@router.get("/", response_model=List[UserOut])
def read_all_users(
    db: Session = Depends(get_db), 
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """Returns a list of all users (Admin only)."""
    # Note: get_current_admin_user already ensures the user is an admin,
    # and if not, it raises a 403 Forbidden error.
    
    users = db.query(UserModel).all()
    return users