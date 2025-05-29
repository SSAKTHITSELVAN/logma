# Updated CustomerCompany Model
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class CustomerCompany(Base):
    __tablename__ = "customer_company"

    customer_company_id = Column(Integer, primary_key=True, index=True)
    
    # Basic identity
    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    
    # Contact details
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=True)
    
    # Address details
    factory_location = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Business details
    contract_type = Column(String(50))  # e.g. Fixed, Variable, On-Demand
    contact_details = Column(Text)      # Additional contact information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trip_allocations = relationship("Trip_Allocation", back_populates="customer_company")

    def __repr__(self):
        return f"<CustomerCompany(id={self.customer_company_id}, name='{self.name}')>"