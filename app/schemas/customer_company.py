# schemas/customer_company.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class CustomerCompanyBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    factory_location: Optional[str] = None
    contract_type: Optional[str] = None
    contact_details: Optional[str] = None

class CustomerCompanyCreate(CustomerCompanyBase):
    pass

class CustomerCompanyUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    factory_location: Optional[str] = None
    contract_type: Optional[str] = None
    contact_details: Optional[str] = None

class CustomerCompany(CustomerCompanyBase):
    customer_company_id: int  # Changed from 'id' to match model
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # Use orm_mode for Pydantic v1
        # from_attributes = True  # This is for Pydantic v2

class CustomerCompanyList(BaseModel):
    companies: List[CustomerCompany]
    total: int
    skip: int
    limit: int