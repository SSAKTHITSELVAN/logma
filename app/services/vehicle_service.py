# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update, delete
# from sqlalchemy.orm import selectinload
# from app.models.vehicle import Vehicle
# from app.schemas.vehicle import VehicleCreate, VehicleUpdate
# from typing import List, Optional
# import asyncio

# class AsyncVehicleService:
#     def __init__(self, db: AsyncSession):
#         self.db = db
    
#     async def get_vehicles(
#         self, 
#         skip: int = 0, 
#         limit: int = 100, 
#         status: Optional[str] = None, 
#         daily_status: Optional[str] = None
#     ) -> List[Vehicle]:
#         query = select(Vehicle)

#         if status:
#             query = query.where(Vehicle.status == status)
#         if daily_status:
#             query = query.where(Vehicle.daily_status == daily_status)

#         query = query.offset(skip).limit(limit)
#         result = await self.db.execute(query)
#         return result.scalars().all()
    
#     async def get_vehicle(self, vehicle_id: int) -> Optional[Vehicle]:
#         query = select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
#         result = await self.db.execute(query)
#         return result.scalar_one_or_none()
    
#     async def get_vehicle_by_vehicle_number(self, vehicle_number: str) -> Optional[Vehicle]:
#         query = select(Vehicle).where(Vehicle.vehicle_number == vehicle_number)
#         result = await self.db.execute(query)
#         return result.scalar_one_or_none()
    
#     async def create_vehicle(self, vehicle: VehicleCreate) -> Vehicle:
#         db_vehicle = Vehicle(**vehicle.dict())
#         self.db.add(db_vehicle)
#         await self.db.commit()
#         await self.db.refresh(db_vehicle)
#         return db_vehicle
    
#     async def update_vehicle(self, vehicle_id: int, vehicle: VehicleUpdate) -> Optional[Vehicle]:
#         db_vehicle = await self.get_vehicle(vehicle_id)
#         if not db_vehicle:
#             return None
            
#         for field, value in vehicle.dict(exclude_unset=True).items():
#             setattr(db_vehicle, field, value)
            
#         await self.db.commit()
#         await self.db.refresh(db_vehicle)
#         return db_vehicle
    
#     async def delete_vehicle(self, vehicle_id: int) -> bool:
#         query = delete(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
#         result = await self.db.execute(query)
#         await self.db.commit()
#         return result.rowcount > 0
    
#     async def get_available_vehicles_today(self) -> List[Vehicle]:
#         query = select(Vehicle).where(
#             Vehicle.status == "active",
#             Vehicle.daily_status == "available"
#         )
#         result = await self.db.execute(query)
#         return result.scalars().all()
    
#     async def bulk_update_daily_status(self, vehicle_ids: List[int], status: str) -> int:
#         query = update(Vehicle).where(
#             Vehicle.id.in_(vehicle_ids)
#         ).values(daily_status=status)
        
#         result = await self.db.execute(query)
#         await self.db.commit()
#         return result.rowcount
    
#     async def get_vehicles_in_line(self) -> List[Vehicle]:
#         query = select(Vehicle).where(
#             Vehicle.status == "active",
#             Vehicle.daily_status == "in_line"
#         )
#         result = await self.db.execute(query)
#         return result.scalars().all()




from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from app.models.vehicle import Vehicle
from app.models.trip_allocation import Trip_Allocation
from app.models.customer_company import CustomerCompany
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from typing import List, Optional, Dict, Any
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
    
    # NEW METHOD: Get recently allocated customer details for a vehicle
    async def get_recent_customer_allocation_by_vehicle_number(
        self, 
        vehicle_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recently allocated customer details for a vehicle based on vehicle number.
        
        Steps:
        1. Find the vehicle by vehicle_number
        2. Get the most recent trip allocation for that vehicle
        3. Join with customer company details
        4. Return combined information
        """
        
        # Step 1: Find vehicle by vehicle_number
        vehicle = await self.get_vehicle_by_vehicle_number(vehicle_number)
        if not vehicle:
            return None
        
        # Step 2 & 3: Get most recent trip allocation with customer details
        query = (
            select(Trip_Allocation, CustomerCompany)
            .join(CustomerCompany, Trip_Allocation.customer_company_id == CustomerCompany.customer_company_id)
            .where(Trip_Allocation.vehicle_id == vehicle.vehicle_id)
            .order_by(Trip_Allocation.created_at.desc())  # Most recent first
            .limit(1)
        )
        
        result = await self.db.execute(query)
        allocation_and_customer = result.first()
        
        if not allocation_and_customer:
            return {
                "vehicle": {
                    "vehicle_id": vehicle.vehicle_id,
                    "vehicle_number": vehicle.vehicle_number,
                    "registration_number": vehicle.registration_number,
                    "vehicle_type": vehicle.vehicle_type,
                    "status": vehicle.status,
                    "daily_status": vehicle.daily_status
                },
                "recent_allocation": None,
                "customer_details": None,
                "message": "No allocations found for this vehicle"
            }
        
        trip_allocation, customer_company = allocation_and_customer
        
        # Step 4: Return combined information
        return {
            "vehicle": {
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_number": vehicle.vehicle_number,
                "registration_number": vehicle.registration_number,
                "vehicle_type": vehicle.vehicle_type,
                "status": vehicle.status,
                "daily_status": vehicle.daily_status
            },
            "recent_allocation": {
                "trip_allocation_id": trip_allocation.trip_allocation_id,
                "load_tons": trip_allocation.load_tons,
                "factory": trip_allocation.factory,
                "trip_type": trip_allocation.trip_type,
                "trip_date_time": trip_allocation.trip_date_time,
                "transport_manager_name": trip_allocation.transport_manager_name,
                "entry_by_role": trip_allocation.entry_by_role,
                "status": trip_allocation.status,
                "created_at": trip_allocation.created_at,
                "updated_at": trip_allocation.updated_at
            },
            "customer_details": {
                "customer_company_id": customer_company.customer_company_id,
                "name": customer_company.name,
                "contact_person": customer_company.contact_person,
                "phone": customer_company.phone,
                "email": customer_company.email,
                "factory_location": customer_company.factory_location,
                "city": customer_company.city,
                "state": customer_company.state,
                "pincode": customer_company.pincode,
                "contract_type": customer_company.contract_type,
                "contact_details": customer_company.contact_details
            }
        }
    
    # ALTERNATIVE METHOD: Get all allocations for a vehicle (if you need history)
    async def get_all_customer_allocations_by_vehicle_number(
        self, 
        vehicle_number: str,
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Get all customer allocations for a vehicle (most recent first).
        """
        
        # Find vehicle by vehicle_number
        vehicle = await self.get_vehicle_by_vehicle_number(vehicle_number)
        if not vehicle:
            return None
        
        # Get all trip allocations with customer details
        query = (
            select(Trip_Allocation, CustomerCompany)
            .join(CustomerCompany, Trip_Allocation.customer_company_id == CustomerCompany.customer_company_id)
            .where(Trip_Allocation.vehicle_id == vehicle.vehicle_id)
            .order_by(Trip_Allocation.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        allocations_and_customers = result.all()
        
        if not allocations_and_customers:
            return {
                "vehicle": {
                    "vehicle_id": vehicle.vehicle_id,
                    "vehicle_number": vehicle.vehicle_number,
                    "registration_number": vehicle.registration_number,
                    "vehicle_type": vehicle.vehicle_type,
                    "status": vehicle.status,
                    "daily_status": vehicle.daily_status
                },
                "allocations": [],
                "message": "No allocations found for this vehicle"
            }
        
        allocations_list = []
        for trip_allocation, customer_company in allocations_and_customers:
            allocations_list.append({
                "allocation": {
                    "trip_allocation_id": trip_allocation.trip_allocation_id,
                    "load_tons": trip_allocation.load_tons,
                    "factory": trip_allocation.factory,
                    "trip_type": trip_allocation.trip_type,
                    "trip_date_time": trip_allocation.trip_date_time,
                    "transport_manager_name": trip_allocation.transport_manager_name,
                    "entry_by_role": trip_allocation.entry_by_role,
                    "status": trip_allocation.status,
                    "created_at": trip_allocation.created_at,
                    "updated_at": trip_allocation.updated_at
                },
                "customer": {
                    "customer_company_id": customer_company.customer_company_id,
                    "name": customer_company.name,
                    "contact_person": customer_company.contact_person,
                    "phone": customer_company.phone,
                    "email": customer_company.email,
                    "factory_location": customer_company.factory_location,
                    "city": customer_company.city,
                    "state": customer_company.state,
                    "pincode": customer_company.pincode,
                    "contract_type": customer_company.contract_type,
                    "contact_details": customer_company.contact_details
                }
            })
        
        return {
            "vehicle": {
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_number": vehicle.vehicle_number,
                "registration_number": vehicle.registration_number,
                "vehicle_type": vehicle.vehicle_type,
                "status": vehicle.status,
                "daily_status": vehicle.daily_status
            },
            "allocations": allocations_list,
            "total_allocations": len(allocations_list)
        }