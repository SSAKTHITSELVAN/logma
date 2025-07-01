# # vehicle.py (router)
# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List, Optional
# from app.database import get_async_db
# from app.schemas.vehicle import Vehicle, VehicleCreate, VehicleUpdate, VehicleOut
# from app.services.vehicle_service import AsyncVehicleService

# router = APIRouter()

# @router.get("/", response_model=List[VehicleOut])
# async def get_vehicles(
#     skip: int = 0,
#     limit: int = 100,
#     status: Optional[str] = Query(None, description="Filter by vehicle status"),
#     daily_status: Optional[str] = Query(None, description="Filter by daily status"),
#     db: AsyncSession = Depends(get_async_db)
# ):
#     service = AsyncVehicleService(db)
#     return await service.get_vehicles(skip=skip, limit=limit, status=status, daily_status=daily_status)

# @router.get("/available", response_model=List[VehicleOut])
# async def get_available_vehicles(db: AsyncSession = Depends(get_async_db)):
#     service = AsyncVehicleService(db)
#     return await service.get_available_vehicles_today()

# @router.get("/in-line", response_model=List[VehicleOut])
# async def get_vehicles_in_line(db: AsyncSession = Depends(get_async_db)):
#     service = AsyncVehicleService(db)
#     return await service.get_vehicles_in_line()

# @router.get("/{vehicle_id}", response_model=VehicleOut)
# async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_async_db)):
#     service = AsyncVehicleService(db)
#     vehicle = await service.get_vehicle(vehicle_id)
#     if not vehicle:
#         raise HTTPException(status_code=404, detail="Vehicle not found")
#     return vehicle

# @router.post("/", response_model=VehicleOut)
# async def create_vehicle(vehicle: VehicleCreate, db: AsyncSession = Depends(get_async_db)):
#     service = AsyncVehicleService(db)
#     # Fixed: Check if vehicle_number already exists (not vehicle_id)
#     existing = await service.get_vehicle_by_vehicle_number(vehicle.vehicle_number)
#     if existing:
#         raise HTTPException(status_code=400, detail="Vehicle number already exists")
#     return await service.create_vehicle(vehicle)

# @router.put("/{vehicle_id}", response_model=VehicleOut)
# async def update_vehicle(
#     vehicle_id: int, 
#     vehicle: VehicleUpdate, 
#     db: AsyncSession = Depends(get_async_db)
# ):
#     service = AsyncVehicleService(db)
#     updated_vehicle = await service.update_vehicle(vehicle_id, vehicle)
#     if not updated_vehicle:
#         raise HTTPException(status_code=404, detail="Vehicle not found")
#     return updated_vehicle

# @router.delete("/{vehicle_id}")
# async def delete_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_async_db)):
#     service = AsyncVehicleService(db)
#     if not await service.delete_vehicle(vehicle_id):
#         raise HTTPException(status_code=404, detail="Vehicle not found")
#     return {"message": "Vehicle deleted successfully"}



# vehicle.py (router)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.database import get_async_db
from app.schemas.vehicle import Vehicle, VehicleCreate, VehicleUpdate, VehicleOut
from app.services.vehicle_service import AsyncVehicleService

router = APIRouter()

@router.get("/", response_model=List[VehicleOut])
async def get_vehicles(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by vehicle status"),
    daily_status: Optional[str] = Query(None, description="Filter by daily status"),
    db: AsyncSession = Depends(get_async_db)
):
    service = AsyncVehicleService(db)
    return await service.get_vehicles(skip=skip, limit=limit, status=status, daily_status=daily_status)

@router.get("/available", response_model=List[VehicleOut])
async def get_available_vehicles(db: AsyncSession = Depends(get_async_db)):
    service = AsyncVehicleService(db)
    return await service.get_available_vehicles_today()

@router.get("/in-line", response_model=List[VehicleOut])
async def get_vehicles_in_line(db: AsyncSession = Depends(get_async_db)):
    service = AsyncVehicleService(db)
    return await service.get_vehicles_in_line()

# NEW ENDPOINT: Get recent customer allocation by vehicle number
@router.get("/recent-allocation/{vehicle_number}")
async def get_recent_customer_allocation(
    vehicle_number: str, 
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Get the most recently allocated customer details for a vehicle based on vehicle number.
    
    Args:
        vehicle_number: The vehicle number to search for
        
    Returns:
        Dictionary containing vehicle info, recent allocation, and customer details
        
    Raises:
        HTTPException: 404 if vehicle not found
    """
    service = AsyncVehicleService(db)
    result = await service.get_recent_customer_allocation_by_vehicle_number(vehicle_number)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Vehicle with number '{vehicle_number}' not found"
        )
    
    return result

# NEW ENDPOINT: Get all customer allocations by vehicle number
@router.get("/allocations/{vehicle_number}")
async def get_all_customer_allocations(
    vehicle_number: str,
    limit: int = Query(10, description="Maximum number of allocations to return"),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Get all customer allocations for a vehicle (most recent first).
    
    Args:
        vehicle_number: The vehicle number to search for
        limit: Maximum number of allocations to return (default: 10)
        
    Returns:
        Dictionary containing vehicle info and list of allocations with customer details
        
    Raises:
        HTTPException: 404 if vehicle not found
    """
    service = AsyncVehicleService(db)
    result = await service.get_all_customer_allocations_by_vehicle_number(vehicle_number, limit)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Vehicle with number '{vehicle_number}' not found"
        )
    
    return result

@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_async_db)):
    service = AsyncVehicleService(db)
    vehicle = await service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.post("/", response_model=VehicleOut)
async def create_vehicle(vehicle: VehicleCreate, db: AsyncSession = Depends(get_async_db)):
    service = AsyncVehicleService(db)
    # Fixed: Check if vehicle_number already exists (not vehicle_id)
    existing = await service.get_vehicle_by_vehicle_number(vehicle.vehicle_number)
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle number already exists")
    return await service.create_vehicle(vehicle)

@router.put("/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(
    vehicle_id: int, 
    vehicle: VehicleUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    service = AsyncVehicleService(db)
    updated_vehicle = await service.update_vehicle(vehicle_id, vehicle)
    if not updated_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated_vehicle

@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_async_db)):
    service = AsyncVehicleService(db)
    if not await service.delete_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}