# backend/routers/invoice.py
from utils.pdf_processor import extract_text_from_pdf
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form # type: ignore
import json # type: ignore
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime
from pydantic import BaseModel
from services.openai_service import extract_invoice_data_with_cache

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
    tags=["invoices"],                         # For API documentation  # Makes all routes require login
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

# Get all invoices for the current user - GET /invoices/
@router.post("/", response_model=InvoiceResponse)  # Changed from schemas.Invoice
async def create_invoice(
    file: UploadFile = File(...),
    invoice_data: str = Form("{}"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Parse the invoice_data JSON string
    try:
        invoice_metadata = json.loads(invoice_data)
        # Clean out empty strings (convert to None for nullable DB fields)
        for key in ["amount", "vendor", "invoice_date", "category"]:
            if key in invoice_metadata and invoice_metadata[key] == "":
                invoice_metadata[key] = None

    except json.JSONDecodeError:
        invoice_metadata = {}
    
    # Create the uploads directory if it doesn't exist
    user_upload_dir = f"uploads/{current_user.id}"
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Save the file
    file_path = f"{user_upload_dir}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create invoice in DB - Changed user_id to owner_id to match your model
    db_invoice = Invoice(  # Direct import, not models.Invoice
        file_name=file.filename,
        file_path=file_path,
        owner_id=current_user.id,  # Changed from user_id to owner_id
        **invoice_metadata
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    # Extract data automatically
    try:
        # Extract text from PDF
        invoice_text = extract_text_from_pdf(file_path)
        
        # Use OpenAI to extract structured data
        extracted_data, token_count = extract_invoice_data_with_cache(invoice_text, db_invoice.id)
        
        # Update the invoice with extracted data
        for key, value in extracted_data.items():
            setattr(db_invoice, key, value)
        
        db.commit()
        db.refresh(db_invoice)
    except Exception as e:
        # Log the error but don't fail the upload
        print(f"Error during auto-extraction: {e}")
        # Optionally set a flag that extraction needs to be retried
        db_invoice.needs_extraction = True  # Note: You need to add this column to your model
        db.commit()
    
    return db_invoice

@router.post("/manual", response_model=InvoiceResponse)
async def create_manual_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🚨 Validate required fields
    if not invoice_data.vendor or invoice_data.amount is None or not invoice_data.invoice_date:
        raise HTTPException(status_code=400, detail="Vendor, amount, and invoice date are required.")

    db_invoice = Invoice(
        file_name="(manual entry)",
        file_path=None,
        owner_id=current_user.id,
        **invoice_data.dict()
    )
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
    if invoice.file_path and os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    # Delete the database record
    db.delete(invoice)
    db.commit()
    
    # Return nothing (204 status code)
    return None

@router.post("/{invoice_id}/extract", response_model=InvoiceResponse)
async def extract_invoice_data_endpoint(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract invoice data using AI"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        # 1. Extract text from the PDF
        invoice_text = extract_text_from_pdf(invoice.file_path)
        print(f"\n📄 Extracted text from invoice {invoice_id}:\n{invoice_text[:500]}")


        # 2. Extract data using OpenAI (with caching)
        extracted_data, token_count = extract_invoice_data_with_cache(invoice_text, invoice_id)

        # 3. Safely update fields only if they exist in response
        invoice.vendor = extracted_data.get("vendor") or invoice.vendor

        try:
            amount_val = extracted_data.get("amount")
            if isinstance(amount_val, (int, float, str)):
                invoice.amount = float(amount_val)
        except Exception as e:
            print(f"⚠️ Failed to convert amount: {amount_val} — {e}")

        invoice.invoice_date = extracted_data.get("invoice_date") or invoice.invoice_date
        invoice.category = extracted_data.get("category") or invoice.category

        # 4. Commit changes
        db.commit()
        db.refresh(invoice)

        return invoice

    except Exception as e:
        print(f"❌ Extraction failed for invoice {invoice_id}: {e}")
        print(f"🔍 Invoice text preview:\n{invoice_text[:500]}")
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")