from starlette.testclient import TestClient
from typing import Dict, Any
import uuid # Essential for generating unique test data

# Base data for a sweet product (name will be added dynamically)
BASE_SWEET_DATA = {
    "category": "Fudge",
    "price": 5.99,
    "stock_quantity": 100,
    "description": "Rich, dark chocolate fudge.",
    "is_available": True
}

# Function to generate unique test data for each POST request
def get_unique_sweet_data() -> Dict[str, Any]:
    # Use UUID to ensure a unique name every time this is called
    unique_name = f"Chocolate Fudge {uuid.uuid4()}"
    return {"name": unique_name, **BASE_SWEET_DATA}


# --- 1. CREATE TESTS (POST /api/sweets/) ---

def test_create_sweet_regular_user_fails(client: TestClient, regular_user_auth_headers: Dict[str, str]):
    """
    Test that a regular (non-admin) user cannot create a sweet.
    Expected result: 403 Forbidden.
    """
    response = client.post(
        "/api/sweets/",
        json=get_unique_sweet_data(), # Use unique data
        headers=regular_user_auth_headers 
    )
    
    assert response.status_code == 403
    assert "Only administrators can create sweets." in response.json()["detail"]

def test_create_sweet_admin_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Test that an admin user CAN successfully create a sweet.
    """
    response = client.post(
        "/api/sweets/",
        json=get_unique_sweet_data(), # Use unique data
        headers=admin_auth_headers
    )
    
    assert response.status_code == 201
    
    # Check the returned data structure
    data = response.json()
    assert data["price"] == BASE_SWEET_DATA["price"]
    assert data["id"] is not None
    assert data["owner_id"] is not None


# --- 2. READ TESTS (GET /api/sweets/) ---

def test_get_all_sweets_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """Test that all users (even unauthenticated) can read the list of sweets."""
    # Ensure a sweet exists for the list (using unique data)
    client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    
    response = client.get("/api/sweets/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_single_sweet_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """Test that a single sweet can be retrieved by ID."""
    # 1. Create a sweet to get its ID (using unique data)
    create_response = client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    assert create_response.status_code == 201
    sweet_id = create_response.json()["id"] # Now this key should exist!
    
    # 2. Get the sweet by ID
    get_response = client.get(f"/api/sweets/{sweet_id}")
    
    assert get_response.status_code == 200
    assert get_response.json()["id"] == sweet_id
    assert get_response.json()["price"] == BASE_SWEET_DATA["price"] # Check a base field

def test_get_non_existent_sweet_fails(client: TestClient):
    """Test retrieving a sweet with an ID that doesn't exist returns a 404."""
    # Note: No authentication is needed for a public check
    response = client.get("/api/sweets/99999") 
    assert response.status_code == 404
    assert "Sweet not found" in response.json()["detail"]


# --- 3. UPDATE TESTS (PUT /api/sweets/{sweet_id}) ---

def test_update_sweet_admin_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """Test that an admin can successfully update a sweet."""
    # 1. Create a sweet (using unique data)
    create_response = client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    assert create_response.status_code == 201
    sweet_id = create_response.json()["id"] # Now this key should exist!
    
    # 2. Update data
    UPDATE_DATA = {"price": 7.50, "description": "New richer, updated fudge.", "stock_quantity": 50}
    
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json=UPDATE_DATA,
        headers=admin_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sweet_id
    assert data["price"] == 7.50
    assert data["description"] == "New richer, updated fudge."
    assert data["stock_quantity"] == 50

def test_update_sweet_regular_user_fails(client: TestClient, regular_user_auth_headers: Dict[str, str], admin_auth_headers: Dict[str, str]):
    """Test that a regular user cannot update a sweet."""
    # 1. Create a sweet (needs admin headers, using unique data)
    create_response = client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    assert create_response.status_code == 201
    sweet_id = create_response.json()["id"] # Now this key should exist!

    # 2. Attempt update with regular user
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json={"price": 100.0},
        headers=regular_user_auth_headers
    )
    
    assert response.status_code == 403
    assert "Only administrators can update sweets." in response.json()["detail"]


# --- 4. DELETE TESTS (DELETE /api/sweets/{sweet_id}) ---

def test_delete_sweet_admin_success(client: TestClient, admin_auth_headers: Dict[str, str]):
    """Test that an admin can successfully delete a sweet (204 No Content)."""
    # 1. Create a sweet (using unique data)
    create_response = client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    assert create_response.status_code == 201
    sweet_id = create_response.json()["id"] # Now this key should exist!

    # 2. Delete the sweet
    delete_response = client.delete(f"/api/sweets/{sweet_id}", headers=admin_auth_headers)
    assert delete_response.status_code == 204
    
    # 3. Verify it's deleted (attempting to GET should return 404)
    get_response = client.get(f"/api/sweets/{sweet_id}")
    assert get_response.status_code == 404

def test_delete_sweet_regular_user_fails(client: TestClient, regular_user_auth_headers: Dict[str, str], admin_auth_headers: Dict[str, str]):
    """Test that a regular user cannot delete a sweet."""
    # 1. Create a sweet (using unique data)
    create_response = client.post("/api/sweets/", json=get_unique_sweet_data(), headers=admin_auth_headers)
    assert create_response.status_code == 201
    sweet_id = create_response.json()["id"] # Now this key should exist!

    # 2. Attempt delete with regular user
    delete_response = client.delete(f"/api/sweets/{sweet_id}", headers=regular_user_auth_headers)
    assert delete_response.status_code == 403
    assert "Only administrators can delete sweets." in delete_response.json()["detail"]
    
    # 3. Verify the sweet still exists
    get_response = client.get(f"/api/sweets/{sweet_id}")
    assert get_response.status_code == 200