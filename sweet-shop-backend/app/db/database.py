from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# --- MYSQL CONNECTION URL (FINALIZED) ---
# User: root, Password: 1234, DB Name: sweet-shop-management
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/sweet-shop-management"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# SessionLocal class will be used to create a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency to yield a session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()