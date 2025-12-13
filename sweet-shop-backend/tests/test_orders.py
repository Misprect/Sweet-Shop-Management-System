import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db import models
import uuid
from typing import Dict, Any

# --- Helper Function for Creating Unique Sweet Data ---
def get_unique_sweet_data():
    """Generates unique data for sweet creation to prevent name conflicts."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Sweet {unique_id}",
        "description": f"Delicious testing sweet {unique_id}",
        "category": "TestCategory",
        "price": 5.50,
        "stock_quantity": 100,
        "is_available": True
    }

# --- Fixture to Create a Sweet in DB for Testing Orders ---
# NOTE: This fixture is only used to ensure a sweet exists for order testing.
@pytest.fixture
def setup_sweets(client: TestClient, db: Session, admin_token: str):
    """Creates a sweet item required for order testing."""
    sweet_data = get_unique_sweet_data()
    sweet_data["stock_quantity"] = 50
    response = client.post(
        "/api/sweets/", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json=sweet_data
    )
    return response.json()


# --- Core Tests for POST /orders ---

def test_create_order_success(client: TestClient, db: Session, regular_user_token: str, admin_token: str):
    """Tests successful creation of an order and verifies stock deduction."""
    # 1. SETUP: Create two sweets
    sweet_data_1 = get_unique_sweet_data()
    sweet_data_1["stock_quantity"] = 50
    sweet_data_2 = get_unique_sweet_data()
    sweet_data_2["stock_quantity"] = 25
    
    # Use admin token to create the setup sweets
    response_1 = client.post("/api/sweets/", headers={"Authorization": f"Bearer {admin_token}"}, json=sweet_data_1)
    sweet_1 = response_1.json()
    response_2 = client.post("/api/sweets/", headers={"Authorization": f"Bearer {admin_token}"}, json=sweet_data_2)
    sweet_2 = response_2.json()

    # 2. ACTION: Place an order
    order_data = {
        "items": [
            {"sweet_id": sweet_1["id"], "quantity": 10}, 
            {"sweet_id": sweet_2["id"], "quantity": 5}
        ]
    }
    
    response = client.post(
        "/api/orders/",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json=order_data
    )

    # 3. ASSERTION 1: Check HTTP Status and Order Details
    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "Pending"
    # Total price calculation check: (10 * 5.50) + (5 * 5.50) = 55.0 + 27.5 = 82.5
    assert order["total_price"] == 82.50 
    assert len(order["items"]) == 2

    # 4. ASSERTION 2: Verify Stock Deduction in the Database (Transaction integrity)
    db_sweet_1 = db.query(models.Sweet).filter(models.Sweet.id == sweet_1["id"]).first()
    db_sweet_2 = db.query(models.Sweet).filter(models.Sweet.id == sweet_2["id"]).first()
    
    assert db_sweet_1.stock_quantity == 40  # 50 - 10 = 40
    assert db_sweet_2.stock_quantity == 20  # 25 - 5 = 20


def test_create_order_insufficient_stock_fails_transaction(client: TestClient, db: Session, regular_user_token: str, admin_token: str):
    """
    Tests that an order fails if stock is insufficient and stock is NOT deducted (full rollback).
    """
    # 1. SETUP: Create one sweet with low stock
    sweet_data = get_unique_sweet_data()
    sweet_data["stock_quantity"] = 5 
    
    response_sweet = client.post("/api/sweets/", headers={"Authorization": f"Bearer {admin_token}"}, json=sweet_data)
    sweet = response_sweet.json()
    
    original_stock = sweet["stock_quantity"]

    # 2. ACTION: Try to place an order for more than is available (e.g., 6)
    order_data = {"items": [{"sweet_id": sweet["id"], "quantity": 6}]}
    
    response = client.post(
        "/api/orders/",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json=order_data
    )

    # 3. ASSERTION 1: Check Failure
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    # 4. ASSERTION 2: Verify stock was NOT deducted (check database integrity)
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet["id"]).first()
    assert db_sweet.stock_quantity == original_stock # Must still be 5

def test_create_order_sweet_not_found(client: TestClient, regular_user_token: str):
    """Tests that an order fails if a sweet ID does not exist."""
    
    order_data = {"items": [{"sweet_id": 99999, "quantity": 1}]} # Use a non-existent ID
    
    response = client.post(
        "/api/orders/",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json=order_data
    )

    assert response.status_code == 404
    assert "Sweet with ID 99999 not found" in response.json()["detail"]

# --- Tests for GET /orders and GET /orders/{order_id} (Authorization) ---
@pytest.fixture
def setup_orders(client: TestClient, regular_user_token: str, admin_token: str) -> Dict[str, Any]:
    """Helper to place a couple of orders for testing retrieval."""
    # Create necessary sweets first
    sweet_data_a = get_unique_sweet_data()
    sweet_data_a["stock_quantity"] = 100
    sweet_data_b = get_unique_sweet_data()
    sweet_data_b["stock_quantity"] = 100
    
    client.post("/api/sweets/", headers={"Authorization": f"Bearer {admin_token}"}, json=sweet_data_a)
    client.post("/api/sweets/", headers={"Authorization": f"Bearer {admin_token}"}, json=sweet_data_b)
    
    # NOTE: Relying on the DB order might be fragile. Better to use the returned IDs from POST.
    # For now, we assume the first two GET results are the ones we just posted.
    all_sweets = client.get("/api/sweets/").json()
    sweet_a = all_sweets[0] 
    sweet_b = all_sweets[1] 

    # Order 1 (Regular User)
    order_data_1 = {"items": [{"sweet_id": sweet_a["id"], "quantity": 1}]}
    resp_1 = client.post("/api/orders/", headers={"Authorization": f"Bearer {regular_user_token}"}, json=order_data_1)
    
    # Order 2 (Admin User)
    order_data_2 = {"items": [{"sweet_id": sweet_b["id"], "quantity": 2}]}
    resp_2 = client.post("/api/orders/", headers={"Authorization": f"Bearer {admin_token}"}, json=order_data_2)
    
    return {
        "regular_user_order": resp_1.json(),
        "admin_order": resp_2.json(),
        "regular_user_token": regular_user_token,
        "admin_token": admin_token
    }

def test_read_all_orders_as_admin(client: TestClient, setup_orders: dict):
    """Admin should be able to retrieve ALL orders (both theirs and the regular user's)."""
    
    response = client.get(
        "/api/orders/",
        headers={"Authorization": f"Bearer {setup_orders['admin_token']}"}
    )
    
    assert response.status_code == 200
    orders = response.json()
    # Check if both orders placed in the fixture are present
    order_ids = [order["id"] for order in orders]
    assert setup_orders["regular_user_order"]["id"] in order_ids
    assert setup_orders["admin_order"]["id"] in order_ids


def test_read_orders_as_regular_user(client: TestClient, setup_orders: dict):
    """Regular user should only be able to retrieve their own orders."""
    
    response = client.get(
        "/api/orders/",
        headers={"Authorization": f"Bearer {setup_orders['regular_user_token']}"}
    )
    
    assert response.status_code == 200
    orders = response.json()
    
    # Check that only the regular user's order is returned
    assert len(orders) >= 1 # Should at least contain their own
    order_ids = [order["id"] for order in orders]
    assert setup_orders["regular_user_order"]["id"] in order_ids
    assert setup_orders["admin_order"]["id"] not in order_ids # Must NOT see the admin's order


def test_read_specific_order_success_as_owner(client: TestClient, setup_orders: dict):
    """Owner should be able to retrieve their specific order."""
    order_id = setup_orders["regular_user_order"]["id"]
    
    response = client.get(
        f"/api/orders/{order_id}",
        headers={"Authorization": f"Bearer {setup_orders['regular_user_token']}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_read_specific_order_success_as_admin(client: TestClient, setup_orders: dict):
    """Admin should be able to retrieve ANY specific order."""
    order_id = setup_orders["regular_user_order"]["id"] # Try to view the regular user's order
    
    response = client.get(
        f"/api/orders/{order_id}",
        headers={"Authorization": f"Bearer {setup_orders['admin_token']}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_read_specific_order_forbidden_non_owner(client: TestClient, setup_orders: dict, regular_user_token: str):
    # FIX APPLIED: Changed 'user_token' to 'regular_user_token' (must be a user other than the order owner or admin)
    """A non-owner user should NOT be able to retrieve another user's order."""
    # The 'regular_user_token' is now used as the non-owner if the admin placed the order.
    # However, since the fixture places an order for the regular user and one for the admin,
    # we need a *third* user to be the non-owner. Since we only have two users in conftest,
    # we test the regular user trying to view the admin's order, or vice versa, 
    # ensuring the token used here is for a non-owner.
    
    # Let the Regular User (owner of order 1) try to view the Admin's Order (order 2).
    admin_order_id = setup_orders["admin_order"]["id"] 
    
    # The 'regular_user_token' is the non-owner for the admin's order.
    response = client.get(
        f"/api/orders/{admin_order_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    
    assert response.status_code == 403
    assert "Not authorized to view this order." in response.json()["detail"]