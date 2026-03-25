from pydantic import BaseModel, field_validator
from schema.customer_schema import CustomerSchema


class PaginationSchema(BaseModel):
    page:  int = 1
    limit: int = 10

    @field_validator("page")
    @classmethod
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("page must be >= 1")
        return v

    @field_validator("limit")
    @classmethod
    def limit_must_be_valid(cls, v):
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v


class PaginatedResponseSchema(BaseModel):
    data:  list[CustomerSchema]
    total: int
    page:  int
    limit: int

