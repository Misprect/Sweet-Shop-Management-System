from fastapi import FastAPI
from .db.database import Base, engine
from .api.endpoints import auth 

# FIX: Temporarily comment out the table creation so the app can start without 
# connecting to the real database during testing (pytest will use its own setup).
# Base.metadata.create_all(bind=engine) 

app = FastAPI(title="Sweet Shop Management System")

# Include the authentication router
app.include_router(auth.router, prefix="/api")
app.include_router(sweets.router, prefix="/api")