# Updated Vehicle Model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicle"
    
    vehicle_id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(50), unique=True, index=True, nullable=False)
    registration_number = Column(String(20), nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    status = Column(String(20), default="active")  # active/inactive
    daily_status = Column(String(20), default="available")  # in_line/assigned/available
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trip_allocations = relationship("Trip_Allocation", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(id={self.vehicle_id}, number='{self.vehicle_number}', status='{self.status}')>"
