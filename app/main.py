from fastapi import FastAPI
from app.database import Base, async_engine
from app.models.vehicle import Vehicle
from app.models.customer_company import CustomerCompany
from app.models.trip_allocation import Trip_Allocation
from app.api.routers import vehicle
from app.api.routers import customer_company
from app.api.routers import trip_allocation

app = FastAPI()

app.include_router(vehicle.router, prefix="/api/vehicle", tags=['Vehicle Management'])
app.include_router(customer_company.router, prefix="/api/customer", tags=['Customer Company Management'])
app.include_router(trip_allocation.router, prefix="/api/trip_allocation", tags=['Trip Allocations Management'])


@app.get('/')
async def test_route():
    message = 'Endpoints working well'
    return {'message': message}


@app.on_event('startup')
async def create_db_tables():
    async with async_engine.begin() as conn:
        print("----&->   ", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)