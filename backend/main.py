# File: backend/main.py

from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine 
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invoice Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Invoice Analyzer API"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}