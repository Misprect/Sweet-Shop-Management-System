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

# --- 1. POST /sweets (Create Sweet - ADMIN ONLY) ---
@router.post("/", response_model=Sweet, status_code=status.HTTP_201_CREATED)
def create_sweet(
    sweet_in: SweetCreate, 
    db: Session = Depends(get_db),
    # Dependency to ensure only active ADMIN users can create sweets
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


# --- 2. GET /sweets (Read All Sweets - PUBLIC) ---
@router.get("/", response_model=List[Sweet])
def read_sweets(db: Session = Depends(get_db)):
    sweets = db.query(SweetModel).all()
    return sweets


# --- 3. GET /sweets/{sweet_id} (Read Single Sweet - PUBLIC) ---
@router.get("/{sweet_id}", response_model=Sweet)
def read_sweet_by_id(sweet_id: int, db: Session = Depends(get_db)):
    db_sweet = db.query(SweetModel).filter(SweetModel.id == sweet_id).first()
    if db_sweet is None:
        raise HTTPException(status_code=404, detail="Sweet not found")
    return db_sweet


# --- 4. PUT /sweets/{sweet_id} (Update Sweet - ADMIN ONLY) ---
@router.put("/{sweet_id}", response_model=Sweet)
def update_sweet(
    sweet_id: int, 
    sweet_in: SweetUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can update sweets."
        )
    
    db_sweet = db.query(SweetModel).filter(SweetModel.id == sweet_id).first()
    if db_sweet is None:
        raise HTTPException(status_code=404, detail="Sweet not found")

    # Update attributes only if they are provided in sweet_in (exclude_unset=True is key here)
    for key, value in sweet_in.model_dump(exclude_unset=True).items():
        setattr(db_sweet, key, value)

    db.add(db_sweet)
    db.commit()
    db.refresh(db_sweet)
    return db_sweet


# --- 5. DELETE /sweets/{sweet_id} (Delete Sweet - ADMIN ONLY) ---
@router.delete("/{sweet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sweet(
    sweet_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can delete sweets."
        )
        
    db_sweet = db.query(SweetModel).filter(SweetModel.id == sweet_id).first()
    if db_sweet is None:
        raise HTTPException(status_code=404, detail="Sweet not found")

    db.delete(db_sweet)
    db.commit()
