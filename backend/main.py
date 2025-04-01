# File: backend/main.py

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import os

from database import Base, engine 
from routers import auth, invoice

# Create the uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# create the database tables if they don't exist 
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app 
app = FastAPI(title="Invoice Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Add routers for authentication and invoice management
app.include_router(auth.router)
app.include_router(invoice.router)

# Home route
@app.get("/")
async def root():
    return {"message": "Welcome to the Invoice Analyzer API"}

# Health check route
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}