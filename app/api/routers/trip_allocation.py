from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_async_db
from app.schemas.trip_allocation import (
    TripAllocationOut,
    TripAllocationCreate,
    TripAllocationUpdate
)
from app.services.trip_allocation_service import AsyncTripAllocationService

router = APIRouter()

@router.get("/", response_model=List[TripAllocationOut])
async def get_trips(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    service = AsyncTripAllocationService(db)
    return await service.get_trips(skip=skip, limit=limit)

@router.get("/{trip_id}", response_model=TripAllocationOut)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_async_db)):
    service = AsyncTripAllocationService(db)
    trip = await service.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.post("/", response_model=TripAllocationOut)
async def create_trip(trip: TripAllocationCreate, db: AsyncSession = Depends(get_async_db)):
    service = AsyncTripAllocationService(db)
    try:
        return await service.create_trip(trip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{trip_id}", response_model=TripAllocationOut)
async def update_trip(trip_id: int, trip: TripAllocationUpdate, db: AsyncSession = Depends(get_async_db)):
    service = AsyncTripAllocationService(db)
    try:
        updated = await service.update_trip(trip_id, trip)
        if not updated:
            raise HTTPException(status_code=404, detail="Trip not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{trip_id}")
async def delete_trip(trip_id: int, db: AsyncSession = Depends(get_async_db)):
    service = AsyncTripAllocationService(db)
    if not await service.delete_trip(trip_id):
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}