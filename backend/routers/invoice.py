# backend/routers/invoice.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status # type: ignore
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

# Define Pydantic models for request/response
class InvoiceBase(BaseModel):
    vendor: Optional[str] = None
    amount: Optional[float] = None
    invoice_date: Optional[str] = None
    category: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    file_name: str
    upload_date: datetime
    
    class Config:
        from_attributes = True

# Define router
router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)

# Helper function to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from routers.auth import SECRET_KEY, ALGORITHM
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:  # Specify the exception type
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# CRUD Operations
@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create upload directory if it doesn't exist
    upload_dir = f"uploads/{current_user.id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the uploaded file
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Create invoice record in database
    db_invoice = Invoice(
        file_name=file.filename,
        file_path=file_location,
        vendor=invoice_data.vendor,
        amount=invoice_data.amount,
        invoice_date=invoice_data.invoice_date,
        category=invoice_data.category,
        owner_id=current_user.id
    )
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

@router.get("/", response_model=List[InvoiceResponse])
async def read_invoices(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).filter(Invoice.owner_id == current_user.id).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update fields
    for key, value in invoice_data.dict(exclude_unset=True).items():
        setattr(invoice, key, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice

@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == current_user.id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete file if exists
    if os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    # Delete from database
    db.delete(invoice)
    db.commit()
    
    return None