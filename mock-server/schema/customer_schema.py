from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CustomerSchema(BaseModel):
    customer_id:     str
    first_name:      str
    last_name:       str
    email:           EmailStr
    phone:           Optional[str] = None
    address:         Optional[str] = None
    date_of_birth:   Optional[date] = None
    account_balance: Optional[Decimal] = None
    created_at:      Optional[datetime] = None

    @field_validator("customer_id")
    @classmethod
    def customer_id_not_empty(cls, v):
        if not v.strip():
            raise ValueError("customer_id cannot be empty")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name fields cannot be empty")
        return v

    model_config = {"from_attributes": True}
