import os
import requests
import dlt
from sqlalchemy.orm import Session
from datetime import date, datetime

FLASK_BASE_URL = os.getenv("FLASK_BASE_URL", "http://mock-server:5000")
EXCHANGE_TOKEN = os.getenv("EXCHANGE_TOKEN", "")
DATABASE_URL   = os.getenv("DATABASE_URL", "")


def get_auth_headers() -> dict:
    """Returns the Authorization header required by the Flask mock server."""
    return {"Authorization": f"Bearer {EXCHANGE_TOKEN}"}


# ─── dlt resource ─────────────────────────────────────────────────────────────

@dlt.resource(
    name="customers",
    write_disposition="merge",   # upsert — insert if new, update if exists
    primary_key="customer_id",
)
def customers_resource():
    """
    dlt resource that fetches all customers from Flask, page by page.
    Yields each page of records — dlt handles loading them into Postgres.
    """
    page  = 1
    limit = 10

    while True:
        response = requests.get(
            f"{FLASK_BASE_URL}/api/customers",
            params={"page": page, "limit": limit},
            headers=get_auth_headers(),
        )
        response.raise_for_status()
        payload = response.json()

        data  = payload.get("data", [])
        total = payload.get("total", 0)

        if not data:
            break

        yield data   # dlt receives this page and loads it

        # Stop once we've covered all records
        if page * limit >= total:
            break

        page += 1


# ─── dlt pipeline ─────────────────────────────────────────────────────────────

def run_ingestion(db: Session) -> int:
    """
    Runs the dlt pipeline:
      1. customers_resource() fetches from Flask (auto-paginated)
      2. dlt loads into PostgreSQL using merge (upsert) on customer_id
      3. Returns total records processed
    """
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination=dlt.destinations.postgres(DATABASE_URL),
        dataset_name="public",       # uses the public schema in customer_db
    )

    # Fetch all first so we can return the count
    all_customers = []
    page  = 1
    limit = 10

    while True:
        response = requests.get(
            f"{FLASK_BASE_URL}/api/customers",
            params={"page": page, "limit": limit},
            headers=get_auth_headers(),
        )
        response.raise_for_status()
        payload = response.json()

        data  = payload.get("data", [])
        total = payload.get("total", 0)

        if not data:
            break

        all_customers.extend(data)

        if page * limit >= total:
            break

        page += 1

    # Process data types before loading
    for customer in all_customers:
        if "account_balance" in customer and isinstance(customer["account_balance"], str):
            try:
                customer["account_balance"] = float(customer["account_balance"])
            except ValueError:
                customer["account_balance"] = None # Handle conversion errors as needed

        if "date_of_birth" in customer and isinstance(customer["date_of_birth"], str):
            try:
                customer["date_of_birth"] = date.fromisoformat(customer["date_of_birth"])
            except ValueError:
                customer["date_of_birth"] = None

        if "created_at" in customer and isinstance(customer["created_at"], str):
            try:
                # Handle 'Z' for UTC timezone
                customer["created_at"] = datetime.fromisoformat(customer["created_at"].replace('Z', '+00:00'))
            except ValueError:
                customer["created_at"] = None

    # Run dlt pipeline with collected data
    # Type coercion above (float, date, datetime) ensures dlt infers correct
    # column types and avoids the varchar vs numeric mismatch in Postgres.
    pipeline.run(
        all_customers,
        table_name="customers",
        write_disposition="merge",
        primary_key="customer_id",
    )

    return len(all_customers)