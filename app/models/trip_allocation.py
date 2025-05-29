from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Trip_Allocation(Base):
    __tablename__ = "trip_allocation"

    trip_allocation_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.vehicle_id"), nullable=False)
    customer_company_id = Column(Integer, ForeignKey("customer_company.customer_company_id"), nullable=False)
    load_tons = Column(Float, nullable=False)
    factory = Column(String, nullable=False)
    trip_type = Column(String, nullable=False)  # 'single' or 'multiple'
    trip_date_time = Column(DateTime(timezone=False), nullable=False)  # Store as naive datetime
    transport_manager_name = Column(String, nullable=False)
    entry_by_role = Column(String, nullable=False)  # 'TM' or 'TM Assistant'
    status = Column(String(20), default="pending")  # pending, allocated, in_progress, completed, cancelled
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="trip_allocations")
    customer_company = relationship("CustomerCompany", back_populates="trip_allocations")

    def __repr__(self):
        return f"<Trip_Allocation(id={self.trip_allocation_id}, vehicle_id={self.vehicle_id}, status='{self.status}')>"