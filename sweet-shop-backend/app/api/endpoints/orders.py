from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# --- CORRECTED IMPORTS ---
# Import the get_db dependency from the database module
from ...db.database import get_db

# Import the security dependency from the core/security module
from ...core.security import get_current_user 

# Import the database model package
from ...db import models 

# Import Pydantic schemas
from ...schemas.order import OrderCreate, Order as OrderSchema, OrderItemCreate, OrderItem as OrderItemSchema
from ...schemas.user import User as UserSchema
# -------------------------

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# --- 1. POST /orders: Create a new order ---

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Creates a new order for the authenticated user.
    """
    if not order_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be empty. Please include at least one item."
        )

    order_items_to_create = []
    total_price = 0.0
    # 1. First Pass: Check Stock, Calculate Price, and Prepare OrderItems
    for item_in in order_in.items:
        sweet = db.query(models.Sweet).filter(models.Sweet.id == item_in.sweet_id).first()

        # a) Validate Sweet Exists and is Available
        if not sweet or not sweet.is_available:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sweet with ID {item_in.sweet_id} not found or is currently unavailable."
            )

        # b) Validate Stock
        if sweet.stock_quantity < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {sweet.name}. Requested: {item_in.quantity}, Available: {sweet.stock_quantity}"
            )

        # c) Capture Price and Calculate Total
        item_price = sweet.price * item_in.quantity
        total_price += item_price

        # Prepare the OrderItem record data (before order_id is known)
        order_items_to_create.append({
            "sweet_id": sweet.id,
            "quantity": item_in.quantity,
            "price_at_purchase": sweet.price,
            "sweet_model": sweet # Store model reference to update stock later
        })

    # 2. Create the main Order record
    db_order = models.Order(
        owner_id=current_user.id,
        total_price=total_price,
        # status defaults to "Pending"
    )
    db.add(db_order)
    db.commit() # Commit the order to get the primary key (order_id)
    db.refresh(db_order)
    
    # 3. Second Pass: Create OrderItems and Deduct Stock
    for item_data in order_items_to_create:
        sweet_model = item_data.pop("sweet_model") # Retrieve the model reference

        # Create the OrderItem record
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            sweet_id=item_data["sweet_id"],
            quantity=item_data["quantity"],
            price_at_purchase=item_data["price_at_purchase"]
        )
        db.add(db_order_item)
        
        # Deduct the stock
        sweet_model.stock_quantity -= item_data["quantity"]
        db.add(sweet_model) # SQLAlchemy tracks changes automatically, but explicit add is safe

    # 4. Final Commit and Return
    db.commit()
    db.refresh(db_order)
    
    # Reload items relationship to include details for the response model
    db.refresh(db_order, attribute_names=['items'])
    return db_order

# --- 2. GET /orders: Fetch a list of orders ---
@router.get("/", response_model=List[OrderSchema])
def read_orders(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Retrieves a list of orders. 
    Admins see all orders. Regular users see only their own orders.
    """
    
    # 1. Start the query on the Order model
    query = db.query(models.Order)
    
    # 2. Apply authorization filter
    if not current_user.is_admin:
        # If not admin, filter by owner_id (the current user's ID)
        query = query.filter(models.Order.owner_id == current_user.id)
    
    # 3. Execute the query, ordering by creation date descending
    orders = query.order_by(models.Order.created_at.desc()).all()
    return orders

# --- 3. GET /orders/{order_id}: Fetch a single order ---
@router.get("/{order_id}", response_model=OrderSchema)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Retrieves a single order by ID.
    Access is restricted to the owner of the order or an Admin user.
    """
    
    # 1. Fetch the order
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    # 2. Check if the order exists
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
        
    # 3. Apply authorization check (Owner OR Admin)
    # Check if the current user is neither the owner nor an admin
    if db_order.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order."
        )     
    return db_order