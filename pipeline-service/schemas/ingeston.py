from pydantic import BaseModel

class IngestResponse(BaseModel):
    """Response after running ingestion pipeline."""
    status: str
    records_processed: int