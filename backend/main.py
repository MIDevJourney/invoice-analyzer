# File: main.py

from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

fake_items = []
@app.post("/items/")
async def create_item(item: Item):
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price must be a positive number")
    fake_items.append({"name": item.name, "price": item.price})
    return item