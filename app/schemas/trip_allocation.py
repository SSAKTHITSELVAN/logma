from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TripAllocationBase(BaseModel):
    vehicle_id: int = Field(..., description="ID of the vehicle")
    company_id: int = Field(..., description="ID of the customer company")
    load_tons: float = Field(..., gt=0, description="Load in tons")
    factory: str = Field(..., min_length=1, description="Factory name")
    trip_type: str = Field(..., description="Trip type: 'single' or 'multiple'")
    trip_date_time: datetime = Field(..., description="Trip date and time")
    transport_manager_name: str = Field(..., min_length=1, description="Transport manager name")
    entry_by_role: str = Field(..., description="Entry role: 'TM' or 'TM Assistant'")

    @validator('trip_type')
    def validate_trip_type(cls, v):
        """Validate trip type is either 'single' or 'multiple'"""
        if v not in ['single', 'multiple']:
            raise ValueError("Trip type must be either 'single' or 'multiple'")
        return v

    @validator('entry_by_role')
    def validate_entry_by_role(cls, v):
        """Validate entry role is either 'TM' or 'TM Assistant'"""
        if v not in ['TM', 'TM Assistant']:
            raise ValueError("Entry role must be either 'TM' or 'TM Assistant'")
        return v

    @validator('trip_date_time')
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility"""
        if v and v.tzinfo is not None:
            # Convert to naive datetime by removing timezone info
            return v.replace(tzinfo=None)
        return v

class TripAllocationCreate(TripAllocationBase):
    """Schema for creating a new trip allocation"""
    pass

class TripAllocationOut(BaseModel):
    """Schema for trip allocation output"""
    trip_allocation_id: int
    vehicle_id: int
    customer_company_id: int  # This matches the database field name
    load_tons: float
    factory: str
    trip_type: str
    trip_date_time: datetime
    transport_manager_name: str
    entry_by_role: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class TripAllocationUpdate(BaseModel):
    """Schema for updating trip allocation - all fields optional"""
    vehicle_id: Optional[int] = Field(None, description="ID of the vehicle")
    company_id: Optional[int] = Field(None, description="ID of the customer company")
    load_tons: Optional[float] = Field(None, gt=0, description="Load in tons")
    factory: Optional[str] = Field(None, min_length=1, description="Factory name")
    trip_type: Optional[str] = Field(None, description="Trip type")
    trip_date_time: Optional[datetime] = Field(None, description="Trip date and time")
    transport_manager_name: Optional[str] = Field(None, min_length=1, description="Transport manager name")
    entry_by_role: Optional[str] = Field(None, description="Entry role")
    status: Optional[str] = Field(None, description="Trip status")

    @validator('trip_type')
    def validate_trip_type(cls, v):
        """Validate trip type is either 'single' or 'multiple'"""
        if v is not None and v not in ['single', 'multiple']:
            raise ValueError("Trip type must be either 'single' or 'multiple'")
        return v

    @validator('entry_by_role')
    def validate_entry_by_role(cls, v):
        """Validate entry role is either 'TM' or 'TM Assistant'"""
        if v is not None and v not in ['TM', 'TM Assistant']:
            raise ValueError("Entry role must be either 'TM' or 'TM Assistant'")
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate status is valid"""
        valid_statuses = ['pending', 'allocated', 'in_progress', 'completed', 'cancelled']
        if v is not None and v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @validator('trip_date_time')
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility"""
        if v and v.tzinfo is not None:
            # Convert to naive datetime by removing timezone info
            return v.replace(tzinfo=None)
        return v