# routers/customer_company.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_async_db
from app.schemas.customer_company import (
    CustomerCompany, 
    CustomerCompanyCreate, 
    CustomerCompanyUpdate,
    CustomerCompanyList
)
from app.services.customer_company_service import AsyncCustomerCompanyService

router = APIRouter()

@router.get("/", response_model=CustomerCompanyList)
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by company name, contact person, location, phone, or email"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    contract_type: Optional[str] = Query(None, description="Filter by contract type"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all companies with pagination and filtering options.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search across multiple fields
    - **city**: Filter by specific city
    - **state**: Filter by specific state
    - **contract_type**: Filter by contract type
    """
    service = AsyncCustomerCompanyService(db)
    return await service.get_companies(
        skip=skip, 
        limit=limit, 
        search=search,
        city=city,
        state=state,
        contract_type=contract_type
    )

@router.get("/search", response_model=List[CustomerCompany])
async def search_companies(
    name: str = Query(..., min_length=1, description="Company name to search (minimum 1 character)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search companies by name with partial matching.
    
    - **name**: Company name to search for (partial match)
    - **limit**: Maximum number of results to return
    """
    service = AsyncCustomerCompanyService(db)
    return await service.search_companies_by_name(name, limit)


@router.get("/{company_id}", response_model=CustomerCompany)
async def get_company(
    company_id: int = Path(..., gt=0, description="Company ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a specific company by ID.
    
    - **company_id**: The ID of the company to retrieve
    """
    service = AsyncCustomerCompanyService(db)
    company = await service.get_company(company_id)
    if not company:
        raise HTTPException(
            status_code=404, 
            detail=f"Company with ID {company_id} not found"
        )
    return company

@router.post("/", response_model=CustomerCompany, status_code=201)
async def create_company(
    company: CustomerCompanyCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new company.
    
    - **name**: Company name (required)
    - **phone**: Contact phone number (required)
    - **contact_person**: Primary contact person
    - **email**: Company email address
    - **address**: Full postal address
    - **city**: City location
    - **state**: State location
    - **pincode**: Postal code
    - **factory_location**: Factory or main location
    - **contract_type**: Type of contract (Fixed, Variable, On-Demand, Hybrid)
    - **contact_details**: Additional contact information
    """
    service = AsyncCustomerCompanyService(db)
    return await service.create_company(company)

@router.put("/{company_id}", response_model=CustomerCompany)
async def update_company(
    company_id: int = Path(..., gt=0, description="Company ID"),
    company: CustomerCompanyUpdate = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update an existing company.
    
    - **company_id**: The ID of the company to update
    - Only provided fields will be updated
    """
    service = AsyncCustomerCompanyService(db)
    updated_company = await service.update_company(company_id, company)
    if not updated_company:
        raise HTTPException(
            status_code=404, 
            detail=f"Company with ID {company_id} not found"
        )
    return updated_company

@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: int = Path(..., gt=0, description="Company ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a company.
    
    - **company_id**: The ID of the company to delete
    """
    service = AsyncCustomerCompanyService(db)
    success = await service.delete_company(company_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Company with ID {company_id} not found"
        )

@router.get("/name/{company_name}", response_model=CustomerCompany)
async def get_company_by_name(
    company_name: str = Path(..., min_length=1, description="Exact company name"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a company by exact name match.
    
    - **company_name**: The exact name of the company
    """
    service = AsyncCustomerCompanyService(db)
    company = await service.get_company_by_name(company_name)
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company with name '{company_name}' not found"
        )
    return company