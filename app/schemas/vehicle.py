# vehicle.py (schemas)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VehicleBase(BaseModel):
    vehicle_number: str
    registration_number: str
    vehicle_type: str
    status: str = "active"
    daily_status: str = "available"

class VehicleCreate(VehicleBase):
    class Config:
        from_attributes = True

class VehicleOut(VehicleBase):
    vehicle_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class VehicleUpdate(BaseModel):
    vehicle_number: Optional[str] = None
    registration_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    status: Optional[str] = None
    daily_status: Optional[str] = None

class Vehicle(VehicleBase):
    vehicle_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True