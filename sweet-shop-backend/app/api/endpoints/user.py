from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

# Import your dependencies
from ...db.database import get_db
from ...db.models import User as UserModel
from ...schemas.user import UserOut # Import UserOut schema from the schemas folder
from ...core.security import get_current_active_user, get_current_admin_user 

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

# --- 1. GET /user/me (Get Current User Profile) ---
@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """Returns the profile of the currently logged-in active user."""
    return current_user

# --- 2. GET /user/all (Admin only) ---
@router.get("/all", response_model=List[UserOut])
def read_all_users(
    db: Session = Depends(get_db), 
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """Returns a list of all users (Admin only)."""
    users = db.query(UserModel).all()
    return users