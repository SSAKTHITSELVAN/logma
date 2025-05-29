from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from fastapi import HTTPException
import logging

from app.models.trip_allocation import Trip_Allocation
from app.models.vehicle import Vehicle
from app.models.customer_company import CustomerCompany
from app.schemas.trip_allocation import (
    TripAllocationCreate,
    TripAllocationUpdate
)

logger = logging.getLogger(__name__)

class AsyncTripAllocationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate_vehicle_exists(self, vehicle_id: int) -> Vehicle:
        """Validate that vehicle exists and return it"""
        query = select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
        result = await self.db.execute(query)
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            raise HTTPException(
                status_code=404, 
                detail=f"Vehicle with ID {vehicle_id} not found"
            )
        return vehicle

    async def _validate_company_exists(self, company_id: int) -> CustomerCompany:
        """Validate that customer company exists and return it"""
        query = select(CustomerCompany).where(CustomerCompany.customer_company_id == company_id)
        result = await self.db.execute(query)
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=404, 
                detail=f"Customer Company with ID {company_id} not found"
            )
        return company

    async def _validate_vehicle_availability(self, vehicle_id: int, exclude_trip_id: Optional[int] = None) -> None:
        """Check if vehicle is available for allocation"""
        vehicle = await self._validate_vehicle_exists(vehicle_id)
        
        # Check if vehicle is active
        if vehicle.status != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_number} is not active (status: {vehicle.status})"
            )
        
        # Check if vehicle is available today
        if vehicle.daily_status not in ["available", "in_line"]:
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_number} is not available (daily status: {vehicle.daily_status})"
            )
        
        # Check for existing active trip allocations
        query = select(Trip_Allocation).where(
            Trip_Allocation.vehicle_id == vehicle_id,
            Trip_Allocation.status.in_(["pending", "in_progress", "allocated"])
        )
        
        if exclude_trip_id:
            query = query.where(Trip_Allocation.trip_allocation_id != exclude_trip_id)
        
        result = await self.db.execute(query)
        existing_trip = result.scalar_one_or_none()
        
        if existing_trip:
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_number} is already allocated to another active trip"
            )

    async def get_trips(self, skip: int = 0, limit: int = 100) -> List[Trip_Allocation]:
        """Get all trips with pagination"""
        try:
            query = select(Trip_Allocation).offset(skip).limit(limit)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting trips: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving trips")

    async def get_trip(self, trip_id: int) -> Optional[Trip_Allocation]:
        """Get a single trip by ID"""
        try:
            query = select(Trip_Allocation).where(Trip_Allocation.trip_allocation_id == trip_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting trip {trip_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving trip")

    async def create_trip(self, trip: TripAllocationCreate) -> Trip_Allocation:
        """Create a new trip allocation with validation"""
        try:
            # Validate vehicle exists and is available
            await self._validate_vehicle_availability(trip.vehicle_id)
            
            # Validate customer company exists (using correct field name)
            await self._validate_company_exists(trip.company_id)
            
            # Create the trip with corrected field mapping
            trip_data = trip.dict()
            # Map company_id to customer_company_id for the database model
            trip_data['customer_company_id'] = trip_data.pop('company_id')
            
            db_trip = Trip_Allocation(**trip_data)
            self.db.add(db_trip)
            await self.db.commit()
            await self.db.refresh(db_trip)
            
            logger.info(f"Created trip allocation: ID {db_trip.trip_allocation_id}")
            return db_trip
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating trip: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating trip allocation")

    async def update_trip(self, trip_id: int, trip: TripAllocationUpdate) -> Optional[Trip_Allocation]:
        """Update an existing trip allocation with validation"""
        try:
            db_trip = await self.get_trip(trip_id)
            if not db_trip:
                return None

            # Get update data
            update_data = trip.dict(exclude_unset=True)
            
            # Validate vehicle if it's being updated
            if 'vehicle_id' in update_data:
                await self._validate_vehicle_availability(
                    update_data['vehicle_id'], 
                    exclude_trip_id=trip_id
                )
            
            # Validate customer company if it's being updated
            if 'company_id' in update_data:
                await self._validate_company_exists(update_data['company_id'])
                # Map company_id to customer_company_id for the database model
                update_data['customer_company_id'] = update_data.pop('company_id')
            
            # Update only provided fields
            for field, value in update_data.items():
                setattr(db_trip, field, value)

            await self.db.commit()
            await self.db.refresh(db_trip)
            
            logger.info(f"Updated trip allocation: ID {trip_id}")
            return db_trip
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating trip {trip_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating trip allocation")

    async def delete_trip(self, trip_id: int) -> bool:
        """Delete a trip allocation"""
        try:
            query = delete(Trip_Allocation).where(Trip_Allocation.trip_allocation_id == trip_id)
            result = await self.db.execute(query)
            await self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deleted trip allocation: ID {trip_id}")
                return True
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting trip {trip_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting trip allocation")

    async def get_trips_by_vehicle(self, vehicle_id: int) -> List[Trip_Allocation]:
        """Get all trips for a specific vehicle"""
        try:
            query = select(Trip_Allocation).where(Trip_Allocation.vehicle_id == vehicle_id)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting trips for vehicle {vehicle_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving vehicle trips")

    async def get_trips_by_company(self, company_id: int) -> List[Trip_Allocation]:
        """Get all trips for a specific customer company"""
        try:
            query = select(Trip_Allocation).where(Trip_Allocation.customer_company_id == company_id)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting trips for company {company_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving company trips")

    async def get_active_trips(self) -> List[Trip_Allocation]:
        """Get all active trip allocations"""
        try:
            # Note: The model doesn't have a status field, so this might need adjustment
            # based on your actual business logic for determining "active" trips
            query = select(Trip_Allocation)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting active trips: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving active trips")