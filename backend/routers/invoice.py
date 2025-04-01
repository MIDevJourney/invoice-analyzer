# backend/routers/invoice.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
import json # type: ignore
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.invoice import Invoice
from models.user import User
from routers.auth import oauth2_scheme, get_user_by_email
from jose import jwt # type: ignore

# These models define what data we accept and return for invoices
class InvoiceBase(BaseModel):
    # Base structure for invoice data - all fields optional so they can be updated individually
    vendor: Optional[str] = None        # Company that issued the invoice
    amount: Optional[float] = None      # How much money the invoice is for
    invoice_date: Optional[str] = None  # When the invoice was issued
    category: Optional[str] = None      # Type of expense (like "Utilities" or "Office Supplies")

class InvoiceCreate(InvoiceBase):
    # Used when creating new invoices - inherits everything from base
    pass

class InvoiceUpdate(InvoiceBase):
    # Used when updating existing invoices - allows partial updates
    pass

class InvoiceResponse(InvoiceBase):
    # What we send back to the user after operations
    id: int                # Database ID for the invoice
    file_name: str         # Name of the uploaded file
    upload_date: datetime  # When the user uploaded it
    
    class Config:
        # Tells Pydantic to convert from database model to this model automatically
        from_attributes = True

# Set up the router with prefix and security
router = APIRouter(
    prefix="/invoices",                        # All routes start with /invoices
    tags=["invoices"],                         # For API documentation
    dependencies=[Depends(oauth2_scheme)],     # Makes all routes require login
    responses={404: {"description": "Not found"}}
)

# Helper to get the current logged-in user from their token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Gets the user info from the login token
    from routers.auth import SECRET_KEY, ALGORITHM
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to get the user's email
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    # Find the user in the database
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Upload a new invoice - POST /invoices/
@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    file: UploadFile = File(...),
    invoice_data: str = Form(...),  # Accept as form field
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Parse the form data
    invoice_data_dict = json.loads(invoice_data)
    invoice_data_model = InvoiceCreate(**invoice_data_dict)
    
    # Create a folder for this user's uploads if it doesn't exist
    upload_dir = f"uploads/{current_user.id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file to the user's folder
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Create a database record for this invoice
    db_invoice = Invoice(
        file_name=file.filename,
        file_path=file_location,
        vendor=invoice_data_model.vendor,
        amount=invoice_data_model.amount,
        invoice_date=invoice_data_model.invoice_date,
        category=invoice_data_model.category,
        owner_id=current_user.id
    )
    
    # Save to database
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

# Get all invoices for the current user - GET /invoices/
@router.get("/", response_model=List[InvoiceResponse])
async def read_invoices(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find all invoices for this user, with pagination options
    invoices = db.query(Invoice).filter(Invoice.owner_id == current_user.id).offset(skip).limit(limit).all()
    return invoices

# Get a specific invoice - GET /invoices/{invoice_id}
@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the invoice by ID, but only if it belongs to this user (security!)
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    
    # If not found or not owned by this user, return 404
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

# Update an invoice - PUT /invoices/{invoice_id}
@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the invoice, checking ownership
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update only the fields that were provided
    for key, value in invoice_data.dict(exclude_unset=True).items():
        setattr(invoice, key, value)
    
    # Save changes
    db.commit()
    db.refresh(invoice)
    
    return invoice

# Delete an invoice - DELETE /invoices/{invoice_id}
@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the invoice, checking ownership
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete the actual file from storage
    if os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    # Delete the database record
    db.delete(invoice)
    db.commit()
    
    # Return nothing (204 status code)
    return None