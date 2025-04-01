#File: backend/models/invoice.py 

from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
import datetime

from ..database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Extracted data
    vendor = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    invoice_date = Column(String, nullable=True)
    category = Column(String, nullable=True)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship with user
    owner = relationship("User", back_populates="invoices")