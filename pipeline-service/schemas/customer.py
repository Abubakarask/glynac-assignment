from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from schemas.general import PaginationRequest, PaginationResponse


# ─── Customer Schemas ─────────────────────────────────────────────────────────

class CustomerResponse(BaseModel):
    """Schema for a single customer in API responses."""
    customer_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    account_balance: Optional[Decimal] = None
    platform_created_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Response Wrappers ────────────────────────────────────────────────────────

class PaginatedCustomerResponse(BaseModel):
    """Paginated list of customers."""
    data: list[CustomerResponse]
    meta: PaginationResponse


class SingleCustomerResponse(BaseModel):
    """Single customer detail."""
    data: CustomerResponse

