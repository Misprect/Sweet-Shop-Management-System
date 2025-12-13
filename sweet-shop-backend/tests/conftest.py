import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from typing import Dict # Added for type hinting clarity

# This allows imports like 'from app.main import app' to resolve correctly 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORTS FROM YOUR PROJECT ---
from app.main import app
from app.db.database import get_db
# Import the base class for model creation (check your structure if Base is in database.py)
from app.db.models import Base 
# ---------------------------------

# --- 1. SETUP THE TEST DATABASE ENGINE ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a new database engine for the entire test session."""
    return create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

@pytest.fixture(scope="session")
def setup_db(engine):
    """
    Creates all tables before the tests run and drops them after the session ends.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function") # Changed scope to 'function' for better isolation!
def session(engine, setup_db):
    """
    Creates a new database session, rolls back at the end of the test.
    We use 'function' scope to ensure fresh data for every single test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


# --- FIXTURE ALIASES (Fixes 'db' not found error) ---
# The tests in test_orders.py expect a 'db' fixture, but you called it 'session'.
# This aliases the 'session' fixture to 'db'.
@pytest.fixture(scope="function")
def db(session):
    yield session


# --- 2. OVERRIDE THE FastAPI DEPENDENCY ---
def override_get_db_dependency(db): # Changed parameter name to 'db' for consistency
    """A closure to return a generator that yields the test session."""
    def _get_db_override():
        try:
            yield db
        finally:
            pass 
    return _get_db_override


# --- 3. TEST CLIENT FIXTURE ---
# Changed scope to 'function' to ensure a fresh client and DB override for each test.
@pytest.fixture(scope="function") 
def client(db):
    """
    Creates a TestClient that uses the overridden database dependency.
    """
    app.dependency_overrides[get_db] = override_get_db_dependency(db)

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# --- 4. AUTHENTICATION FIXTURES ---
# Changed scope to 'function' so users are re-registered for each test group, ensuring the admin status is always correct.

@pytest.fixture(scope="function")
def admin_user_data() -> Dict[str, str]:
    """Returns data for the initial (admin) user."""
    return {
        "email": "admin@sweetshop.com",
        "password": "securepassword123"
    }

@pytest.fixture(scope="function")
def regular_user_data() -> Dict[str, str]:
    """Returns data for the regular user."""
    return {
        "email": "user@sweetshop.com",
        "password": "userpassword123"
    }

@pytest.fixture(scope="function")
def admin_auth_headers(client: TestClient, admin_user_data: Dict[str, str]) -> Dict[str, str]: 
    """Registers the first user (admin) and logs them in, returning authorization headers."""
    # 1. Register the admin user
    # NOTE: This ensures the user is the FIRST user, making them an admin per auth.py logic
    client.post("/api/auth/register", json=admin_user_data)
    
    # 2. Log in the admin user to get a token
    response = client.post(
        "/api/auth/token",
        data={"username": admin_user_data["email"], "password": admin_user_data["password"]},
    )
    
    # Check if the token creation was successful (debug)
    if response.status_code != 200:
        raise Exception(f"Admin login failed with status {response.status_code}: {response.json()}")

    # 3. Extract the token and format the header
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
    
@pytest.fixture(scope="function")
def regular_user_auth_headers(client: TestClient, admin_auth_headers: Dict[str, str], regular_user_data: Dict[str, str]) -> Dict[str, str]:
    """Registers a second user (regular user) and logs them in."""
    # Dependency on admin_auth_headers ensures the admin is registered first.
    
    # 1. Register the regular user (will not be admin)
    client.post("/api/auth/register", json=regular_user_data)
    
    # 2. Log in the regular user
    response = client.post(
        "/api/auth/token",
        data={"username": regular_user_data["email"], "password": regular_user_data["password"]},
    )
    
    if response.status_code != 200:
        raise Exception(f"Regular user login failed with status {response.status_code}: {response.json()}")
    
    # 3. Extract the token and format the header
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

# --- NEW FIXTURES RETURNING ONLY THE TOKEN STRING (Fixes token not found errors) ---

@pytest.fixture(scope="function")
def admin_token(admin_auth_headers: Dict[str, str]) -> str:
    """Returns just the raw access token string for the admin user."""
    return admin_auth_headers["Authorization"].split(" ")[1]

@pytest.fixture(scope="function")
def regular_user_token(regular_user_auth_headers: Dict[str, str]) -> str:
    """Returns just the raw access token string for the regular user."""
    return regular_user_auth_headers["Authorization"].split(" ")[1]