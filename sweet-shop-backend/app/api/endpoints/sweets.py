from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import your dependencies and database utility
from ...db.database import get_db
from ...schemas.sweet import SweetCreate, Sweet, SweetUpdate
from ...db.models import Sweet as SweetModel, User as UserModel
from ...core.security import get_current_active_user # For admin authorization

router = APIRouter(
    prefix="/sweets",
    tags=["Sweets"]
)

# --- 1.POST /sweets ---
@router.post("/", response_model=Sweet, status_code=status.HTTP_201_CREATED)
def create_sweet(
    sweet_in: SweetCreate, 
    db: Session = Depends(get_db),
    # Only allow active ADMIN users to create sweets
    current_user: UserModel = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can create sweets."
        )

    # Check if a sweet with this name already exists
    db_sweet = db.query(SweetModel).filter(SweetModel.name == sweet_in.name).first()
    if db_sweet:
        raise HTTPException(status_code=400, detail="Sweet with this name already exists")

    # Create the sweet model instance
    db_sweet = SweetModel(**sweet_in.model_dump(), owner_id=current_user.id)
    
    db.add(db_sweet)
    db.commit()
    db.refresh(db_sweet)
    return db_sweet


# --- 2.GET /sweets ---
@router.get("/", response_model=List[Sweet])
def read_sweets(db: Session = Depends(get_db)):
    sweets = db.query(SweetModel).all()
    return sweets
