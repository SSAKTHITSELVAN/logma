from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from typing import List, Optional
import asyncio

class AsyncVehicleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_vehicles(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None, 
        daily_status: Optional[str] = None
    ) -> List[Vehicle]:
        query = select(Vehicle)

        if status:
            query = query.where(Vehicle.status == status)
        if daily_status:
            query = query.where(Vehicle.daily_status == daily_status)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_vehicle(self, vehicle_id: int) -> Optional[Vehicle]:
        query = select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_vehicle_by_vehicle_number(self, vehicle_number: str) -> Optional[Vehicle]:
        query = select(Vehicle).where(Vehicle.vehicle_number == vehicle_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_vehicle(self, vehicle: VehicleCreate) -> Vehicle:
        db_vehicle = Vehicle(**vehicle.dict())
        self.db.add(db_vehicle)
        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle
    
    async def update_vehicle(self, vehicle_id: int, vehicle: VehicleUpdate) -> Optional[Vehicle]:
        db_vehicle = await self.get_vehicle(vehicle_id)
        if not db_vehicle:
            return None
            
        for field, value in vehicle.dict(exclude_unset=True).items():
            setattr(db_vehicle, field, value)
            
        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle
    
    async def delete_vehicle(self, vehicle_id: int) -> bool:
        query = delete(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_available_vehicles_today(self) -> List[Vehicle]:
        query = select(Vehicle).where(
            Vehicle.status == "active",
            Vehicle.daily_status == "available"
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def bulk_update_daily_status(self, vehicle_ids: List[int], status: str) -> int:
        query = update(Vehicle).where(
            Vehicle.id.in_(vehicle_ids)
        ).values(daily_status=status)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount
    
    async def get_vehicles_in_line(self) -> List[Vehicle]:
        query = select(Vehicle).where(
            Vehicle.status == "active",
            Vehicle.daily_status == "in_line"
        )
        result = await self.db.execute(query)
        return result.scalars().all()