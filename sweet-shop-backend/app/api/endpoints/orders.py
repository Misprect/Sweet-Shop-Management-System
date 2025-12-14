from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload 
from sqlalchemy import select 
from typing import List

# --- CORRECTED IMPORTS ---
from ...db.database import get_db
from ...core.security import get_current_user 
from ...db import models 

# NOTE: You MUST ensure these Pydantic schemas exist and OrderAdmin is defined
from ...schemas.order import OrderCreate, Order as OrderSchema, OrderItemCreate, OrderItem as OrderItemSchema, OrderStatusUpdate, OrderAdmin
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
    for item_in in order_in.items:
        sweet = db.query(models.Sweet).filter(models.Sweet.id == item_in.sweet_id).first()

        if not sweet or not sweet.is_available:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sweet with ID {item_in.sweet_id} not found or is currently unavailable."
            )

        if sweet.stock_quantity < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {sweet.name}. Requested: {item_in.quantity}, Available: {sweet.stock_quantity}"
            )

        item_price = sweet.price * item_in.quantity
        total_price += item_price

        order_items_to_create.append({
            "sweet_id": sweet.id,
            "quantity": item_in.quantity,
            "price_at_purchase": sweet.price,
            "sweet_model": sweet 
        })

    db_order = models.Order(
        owner_id=current_user.id,
        total_price=total_price,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for item_data in order_items_to_create:
        sweet_model = item_data.pop("sweet_model") 

        db_order_item = models.OrderItem(
            order_id=db_order.id,
            sweet_id=item_data["sweet_id"],
            quantity=item_data["quantity"],
            price_at_purchase=item_data["price_at_purchase"]
        )
        db.add(db_order_item)
        
        sweet_model.stock_quantity -= item_data["quantity"]
        db.add(sweet_model) 

    db.commit()
    db.refresh(db_order)
    
    # Reload the order with items/sweet names for the response
    db.refresh(db_order, attribute_names=['items'])
    
    # Manually map items to include sweet name before returning
    order_dict = db_order.__dict__.copy()
    items_list_for_pydantic = []
    for item in db_order.items:
        # Check if the sweet relationship exists before accessing name
        if hasattr(item, 'sweet') and item.sweet:
            item_dict = item.__dict__.copy()
            item_dict['name'] = item.sweet.name 
            items_list_for_pydantic.append(item_dict)
        else:
            # Fallback if eager loading failed for some reason
            items_list_for_pydantic.append(item.__dict__.copy())
            
    order_dict['items'] = items_list_for_pydantic
    
    return OrderSchema(**order_dict)


# --- 2. GET /orders: Fetch a list of orders (FINAL WORKING VERSION) ---
@router.get("/", response_model=List[OrderSchema]) 
def read_orders(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Retrieves a list of orders. 
    Admins see all orders with user email. Regular users see only their own orders.
    """
    
    if current_user.is_admin:
        # Admin logic: Fetch all orders, join User for email, and eagerly load nested relationships.
        
        # 1. Define the selection statement: Select ALL Order columns and the joined User email.
        # This uses positional indexing for ultimate reliability.
        stmt = select(
            models.Order,
            models.User.email.label("user_email") # <-- This provides the email at position [1]
        ).join(models.User, models.Order.owner_id == models.User.id) \
          .options(
              # Eagerly load order items and the sweet related to each item
              joinedload(models.Order.items).joinedload(models.OrderItem.sweet) 
          ) \
         .order_by(models.Order.created_at.desc())
         
        # 2. Execute the statement
        result = db.execute(stmt)
        orders_data = result.unique().all() 
        
        orders_list = []
        for row in orders_data:
            # CRITICAL: Order model is at index 0, User email is at index 1
            order_obj = row[0] 
            user_email = row[1] 

            # Convert ORM object to dict 
            order_dict = order_obj.__dict__.copy()
            
            # 3. Map items, including the Sweet Name (now available via the eager load)
            items_list_for_pydantic = []
            for item in order_obj.items:
                item_dict = item.__dict__.copy()
                # CRITICAL: Access the name from the eagerly loaded sweet relationship
                item_dict['name'] = item.sweet.name 
                items_list_for_pydantic.append(item_dict)

            order_dict['items'] = items_list_for_pydantic
            order_dict['user_email'] = user_email # <--- Using the guaranteed user_email
            
            # Pass the combined dictionary to the OrderAdmin schema
            orders_list.append(OrderAdmin(**order_dict)) 
            
        return orders_list
        
    else:
        # Regular User logic: Filter by owner_id (also eagerly load items for performance)
        orders = db.query(models.Order).filter(models.Order.owner_id == current_user.id) \
             .options(
                 joinedload(models.Order.items).joinedload(models.OrderItem.sweet)
             ) \
             .order_by(models.Order.created_at.desc()).all()
             
        # Manually map items to include sweet name for the standard OrderSchema as well
        orders_list = []
        for order_obj in orders:
            order_dict = order_obj.__dict__.copy()
            items_list_for_pydantic = []
            for item in order_obj.items:
                item_dict = item.__dict__.copy()
                item_dict['name'] = item.sweet.name 
                items_list_for_pydantic.append(item_dict)
            order_dict['items'] = items_list_for_pydantic
            orders_list.append(OrderSchema(**order_dict)) 

        return orders_list


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
    
    # Eagerly load items and sweet for single order view
    db_order = db.query(models.Order).filter(models.Order.id == order_id) \
        .options(
            joinedload(models.Order.items).joinedload(models.OrderItem.sweet)
        ).first()
    
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
        
    if db_order.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order."
        )     

    # Map items to include sweet name before returning
    order_dict = db_order.__dict__.copy()
    items_list_for_pydantic = []
    for item in db_order.items:
        item_dict = item.__dict__.copy()
        item_dict['name'] = item.sweet.name 
        items_list_for_pydantic.append(item_dict)
    order_dict['items'] = items_list_for_pydantic
    
    return OrderSchema(**order_dict)


# --- 4. PATCH /orders/{order_id}/status: Update order status (ADMIN ONLY) ---
@router.patch("/{order_id}/status", response_model=OrderSchema)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Updates the status of an order. Restricted to Admin users.
    """
    # 1. Authorization: Only Admin can update status
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update order status."
        )

    # 2. Validation: Check if the new status is valid
    valid_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value. Must be one of: {', '.join(valid_statuses)}"
        )

    # 3. Fetch the order
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )

    # 4. Update and Commit
    db_order.status = status_update.status
    db.add(db_order)
    db.commit()
    
    # Reload the order with items/sweet names for the response
    db_order = db.query(models.Order).filter(models.Order.id == order_id) \
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.sweet)).first()
    
    # Map items to include sweet name before returning
    order_dict = db_order.__dict__.copy()
    items_list_for_pydantic = []
    for item in db_order.items:
        item_dict = item.__dict__.copy()
        item_dict['name'] = item.sweet.name 
        items_list_for_pydantic.append(item_dict)
    order_dict['items'] = items_list_for_pydantic
    
    return OrderSchema(**order_dict)