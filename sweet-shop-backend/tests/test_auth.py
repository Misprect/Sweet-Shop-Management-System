import pytest
# Import TestClient for type hinting, although we use the fixture
from starlette.testclient import TestClient 

# --- TEST 1: Successful Registration ---
# FIX: Removed @pytest.mark.asyncio and 'async' keyword
def test_register_user_success(client: TestClient): 
    """Test successful user registration (first user should be admin)."""
    
    #Setup : define valid user data
    user_data= {
        "email": "testuser@sweetshop.com",
        "password": "securepassword123"
    }
    # FIX: Removed 'await' keyword
    response= client.post("/api/auth/register", json=user_data) 

    # Assertions for a successful registration
    assert response.status_code == 201
    data= response.json()

    # Assertions for the token payload
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_role" in data

    # The first user should be an admin
    assert data["user_role"] == "admin"

# --- TEST 2: Email Already Registered (Failure) ---
# FIX: Removed @pytest.mark.asyncio and 'async' keyword
def test_register_user_email_exists(client: TestClient):
    """Test failure when registering a user with an existing email."""
    
    # Setup: Register the user once
    user_data = {
        "email": "duplicate@sweetshop.com",
        "password": "securepassword123"
    }
    # FIX: Removed 'await' keyword
    client.post("/api/auth/register", json=user_data) 

    #Action: Attempt to register the same user again
    # FIX: Removed 'await' keyword
    response= client.post("/api/auth/register", json=user_data) 

    # Assertions for failure
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"