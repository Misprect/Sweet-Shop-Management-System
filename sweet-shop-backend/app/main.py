from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- ADDED IMPORT
from .db.database import Base, engine
from .api.endpoints import auth 
from .api.endpoints import sweets
from .api.endpoints import user
from .api.endpoints import orders 
from app.db import models

# FIX: Temporarily comment out the table creation so the app can start without 
# connecting to the real database during testing (pytest will use its own setup).
# Base.metadata.create_all(bind=engine) 

app = FastAPI(title="Sweet Shop Management System")

# --- START OF CORS CONFIGURATION ---
# This block allows your frontend (running on a different port) to access the backend API.
origins = [
    # Common frontend development ports
    "http://localhost:5173", # Often used by Vite/React/Vue/Svelte
    "http://127.0.0.1:5173",
    "http://localhost:3000", # Often used by Create React App
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers needed for communication
)
# --- END OF CORS CONFIGURATION ---

# Include the authentication router
app.include_router(auth.router, prefix="/api")
app.include_router(sweets.router, prefix="/api") 
app.include_router(user.router, prefix="/api")
app.include_router(orders.router, prefix="/api")