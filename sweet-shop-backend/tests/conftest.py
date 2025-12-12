# sweet-shop-backend/tests/conftest.py

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

# --- PATH FIX: Add the 'sweet-shop-backend' directory to the system path ---
# This allows imports like 'from app.main import app' to resolve correctly 
# by making the 'app' directory available as a package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORTS FROM YOUR PROJECT ---
# Corrected imports based on the structure: app/db/database.py and app/db/models.py
from app.main import app
from app.db.database import get_db
from app.db.models import Base 
# Note: If Base is defined in database.py instead of models.py, 
# you might need to adjust 'from app.db.models import Base' accordingly.

# --- 1. SETUP THE TEST DATABASE ENGINE ---
# Using an in-memory SQLite database for fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a new database engine for the entire test session."""
    return create_engine(
        SQLALCHEMY_DATABASE_URL, 
        # Required for SQLite to run across different threads/scopes
        connect_args={"check_same_thread": False}
    )

@pytest.fixture(scope="session")
def setup_db(engine):
    """
    Creates all tables before the tests run and drops them after the session ends.
    This resolves the "no such table: users" error.
    """
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup: Drop tables after the test session is complete
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def session(engine, setup_db):
    """
    Creates a new database session wrapped in a transaction for each test function.
    The transaction is rolled back at the end of the test for clean state.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    # Bind the session to the connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


# --- 2. OVERRIDE THE FastAPI DEPENDENCY ---
def override_get_db_dependency(session):
    """A closure to return a generator that yields the test session."""
    def _get_db_override():
        try:
            # Yield the session created by the 'session' fixture
            yield session
        finally:
            # The 'session' fixture handles closing and rollback, so we do nothing here
            pass 
    return _get_db_override


# --- 3. TEST CLIENT FIXTURE ---
@pytest.fixture(scope="function")
def client(session):
    """
    Creates a TestClient that uses the overridden database dependency, 
    ensuring every test uses the isolated, transactional session.
    """
    # Override the app's real 'get_db' dependency with our testing session
    app.dependency_overrides[get_db] = override_get_db_dependency(session)

    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up the dependency override after the test
    app.dependency_overrides.clear()