from pydantic import BaseModel, field_validator

# ─── Pagination ───────────────────────────────────────────────────────────────

class PaginationRequest(BaseModel):
    """Validates pagination query parameters."""
    offset: int = 0
    limit: int = 10

    @field_validator("offset")
    @classmethod
    def offset_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("offset must be >= 0")
        return v

    @field_validator("limit")
    @classmethod
    def limit_must_be_valid(cls, v):
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v


class PaginationResponse(BaseModel):
    """Response with pagination metadata."""
    total: int
    offset: int
    limit: int


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
