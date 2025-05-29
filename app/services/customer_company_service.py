# services/customer_company_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_
from sqlalchemy.exc import IntegrityError
from app.models.customer_company import CustomerCompany
from app.schemas.customer_company import (
    CustomerCompanyCreate, 
    CustomerCompanyUpdate, 
    CustomerCompanyList,
    CustomerCompany as CustomerCompanySchema
)
from typing import List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class AsyncCustomerCompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        contract_type: Optional[str] = None
    ) -> CustomerCompanyList:
        """Get companies with pagination and filtering"""
        try:
            query = select(CustomerCompany)
            count_query = select(func.count(CustomerCompany.customer_company_id))
            
            filters = []
            
            if search:
                search_filter = f"%{search.strip()}%"
                search_conditions = or_(
                    CustomerCompany.name.ilike(search_filter),
                    CustomerCompany.contact_person.ilike(search_filter),
                    CustomerCompany.factory_location.ilike(search_filter),
                    CustomerCompany.phone.ilike(search_filter),
                    CustomerCompany.email.ilike(search_filter)
                )
                filters.append(search_conditions)
            
            if city:
                filters.append(CustomerCompany.city.ilike(f"%{city}%"))
            
            if state:
                filters.append(CustomerCompany.state.ilike(f"%{state}%"))
            
            if contract_type:
                filters.append(CustomerCompany.contract_type == contract_type)
            
            if filters:
                filter_condition = and_(*filters)
                query = query.where(filter_condition)
                count_query = count_query.where(filter_condition)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()
            
            query = query.offset(skip).limit(limit).order_by(CustomerCompany.name)
            result = await self.db.execute(query)
            companies = result.scalars().all()
            
            return CustomerCompanyList(
                companies=companies,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error getting companies: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving companies")

    async def get_company(self, company_id: int) -> Optional[CustomerCompany]:
        """Get a single company by ID"""
        try:
            query = select(CustomerCompany).where(CustomerCompany.customer_company_id == company_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting company {company_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving company")

    async def create_company(self, company: CustomerCompanyCreate) -> CustomerCompany:
        """Create a new company"""
        try:
            existing = await self.get_company_by_name(company.name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Company with name '{company.name}' already exists"
                )
            
            db_company = CustomerCompany(**company.dict())  # Changed from dict()
            self.db.add(db_company)
            await self.db.commit()
            await self.db.refresh(db_company)
            
            logger.info(f"Created company: {db_company.name} (ID: {db_company.customer_company_id})")
            return db_company
            
        except HTTPException:
            raise
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating company: {str(e)}")
            raise HTTPException(status_code=400, detail="Company with this information already exists")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating company: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating company")

    async def update_company(
        self,
        company_id: int,
        company: CustomerCompanyUpdate
        ) -> Optional[CustomerCompany]:
        """Update an existing company"""
        try:
            db_company = await self.get_company(company_id)
            if not db_company:
                return None
            
            if company.name and company.name != db_company.name:
                existing = await self.get_company_by_name(company.name)
                if existing and existing.customer_company_id != company_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Company with name '{company.name}' already exists"
                    )
            
            update_data = company.dict(exclude_unset=True)  # Changed from dict()
            for field, value in update_data.items():
                setattr(db_company, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_company)
            
            logger.info(f"Updated company: {db_company.name} (ID: {db_company.customer_company_id})")
            return db_company
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating company {company_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating company")

    async def delete_company(self, company_id: int) -> bool:
        """Delete a company"""
        try:
            db_company = await self.get_company(company_id)
            if not db_company:
                return False
            
            await self.db.delete(db_company)
            await self.db.commit()
            
            logger.info(f"Deleted company: {db_company.name} (ID: {company_id})")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting company {company_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting company")

    async def get_company_by_name(self, name: str) -> Optional[CustomerCompany]:
        """Get company by exact name match"""
        try:
            query = select(CustomerCompany).where(CustomerCompany.name == name)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting company by name '{name}': {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving company")

    async def search_companies_by_name(self, name: str, limit: int = 10) -> List[CustomerCompany]:
        """Search companies by name (partial match)"""
        try:
            query = select(CustomerCompany).where(
                CustomerCompany.name.ilike(f"%{name}%")
            ).limit(limit).order_by(CustomerCompany.name)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching companies by name '{name}': {str(e)}")
            raise HTTPException(status_code=500, detail="Error searching companies")