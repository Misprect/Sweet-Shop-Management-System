import pytest
from httpx import AsyncClient

#fixture setup is handled in conftest.py
##TDD Step 1: Write a test that fails (RED) for User Registration##
@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    #Setup : define valid user data
    user_data= {
        "email": "testuser@sweetshop.com",
        "password": "securepassword123"
    }
    # Action: Attempt to register the user
    # This assumes the endpoint is at /api/auth/register and returns a token
    response= await async_client.post("/api/auth/register", json=user_data)

    # Assertions for a successful registration (HTTP 201 Created is ideal for creation)
    assert response.status_code == 201
    data= response.json()

    # Assertions for the token payload (core requirement)
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_role" in data

    # The first user should be an admin (based on the logic provided previously)
    assert data["user_role"] == "admin"
@pytest.mark.asyncio
async def test_reguster_user_email_exists(async_client: AsyncClient):
    # Setup: Register the user once
    user_data = {
        "email": "duplicate@sweetshop.com",
        "password": "securepassword123"
    }
    await async_client.post("/api/auth/register", json=user_data)

    #Action: Attempt to register the same user again
    response= await async_client.post("/api/auth/register", json=user_data)

    # Assertions for failure
    assert response.status_code == 400
    assert "Email already registered" in response.json().get("detail", "")