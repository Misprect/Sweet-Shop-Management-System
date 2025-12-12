from starlette.testclient import TestClient
from typing import Dict

# Sample data for a sweet product
SWEET_DATA = {
    "name": "Chocolate Fudge",
    "category": "Fudge",
    "price": 5.99,
    "stock_quantity": 100
}

# --- RED TEST 1: Unauthorized Creation (Regular User) ---
def test_create_sweet_regular_user_fails(client: TestClient, regular_user_auth_headers: Dict[str, str]):
    """
    Test that a regular (non-admin) user cannot create a sweet.
    Expected result: 403 Forbidden.
    """
    response = client.post(
        "/api/sweets/",
        json=SWEET_DATA,
        headers=regular_user_auth_headers 
    )
    
    assert response.status_code == 403
    assert "Only administrators can create sweets." in response.json()["detail"]

# --- RED TEST 2: Successful Creation (Admin User) ---
def test_create_sweet_admin_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Test that an admin user CAN successfully create a sweet.
    """
    response = client.post(
        "/api/sweets/",
        json=SWEET_DATA,
        headers=admin_auth_headers
    )
    
    # We expect a 201 Created status code
    assert response.status_code == 201
    
    # Check the returned data structure
    data = response.json()
    assert data["name"] == SWEET_DATA["name"]
    assert data["price"] == SWEET_DATA["price"]
    assert data["id"] is not None
    assert data["owner_id"] is not None