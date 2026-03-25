import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, init_db
from models.customer import Customer
from services.ingestion import run_ingestion
from schemas.customer import (
    CustomerResponse,
    PaginatedCustomerResponse,
    SingleCustomerResponse,
)
from schemas.ingeston import IngestResponse
from schemas.general import HealthResponse, PaginationResponse


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables when the service starts."""
    init_db()
    yield


app = FastAPI(title="Customer Pipeline Service", lifespan=lifespan)


# ─── 1. Ingest ────────────────────────────────────────────────────────────────

@app.post("/api/ingest", response_model=IngestResponse)
def ingest(db: Session = Depends(get_db)):
    """
    Fetches all customers from Flask mock server (handles pagination)
    and upserts them into PostgreSQL.
    """
    try:
        records_processed = run_ingestion(db)
        return IngestResponse(status="success", records_processed=records_processed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 2. List customers ────────────────────────────────────────────────────────

@app.get("/api/customers", response_model=PaginatedCustomerResponse)
def list_customers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return paginated customers from PostgreSQL."""
    total = db.query(Customer).count()
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return PaginatedCustomerResponse(
        data=[CustomerResponse.model_validate(c) for c in customers],
        meta=PaginationResponse(total=total, offset=offset, limit=limit),
    )


# ─── 3. Single customer ───────────────────────────────────────────────────────

@app.get("/api/customers/{customer_id}", response_model=SingleCustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Return a single customer by ID or 404."""
    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return SingleCustomerResponse(data=CustomerResponse.model_validate(customer))


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="pipeline-service")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)