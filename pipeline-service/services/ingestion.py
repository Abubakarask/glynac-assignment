import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from models.customer import Customer

FLASK_BASE_URL = os.getenv("FLASK_URL", "http://localhost:5000")
EXCHANGE_TOKEN = os.getenv("EXCHANGE_TOKEN", "")


def get_auth_headers() -> dict:
    """Returns the Authorization header required by the Flask mock server."""
    return {"Authorization": f"Bearer {EXCHANGE_TOKEN}"}


def fetch_all_customers_from_flask() -> list[dict]:
    """
    Fetches all customers from Flask, handling pagination automatically.
    Keeps requesting pages until all records are collected.
    """
    all_customers = []
    page = 1
    limit = 10

    while True:
        response = requests.get(
            f"{FLASK_BASE_URL}/api/customers",
            params={"page": page, "limit": limit},
            headers=get_auth_headers()
        )
        response.raise_for_status()
        payload = response.json()

        data = payload.get("data", [])
        all_customers.extend(data)

        total = payload.get("total", 0)

        # Stop when we've fetched everything
        if len(all_customers) >= total or len(data) == 0:
            break

        page += 1

    return all_customers


def parse_customer(raw: dict) -> dict:
    """Parse raw dict from Flask into DB-ready values."""
    return {
        "customer_id":     raw["customer_id"],
        "first_name":      raw["first_name"],
        "last_name":       raw["last_name"],
        "email":           raw["email"],
        "phone":           raw.get("phone"),
        "address":         raw.get("address"),
        "date_of_birth":   raw.get("date_of_birth"),   # string, Postgres handles cast
        "account_balance": raw.get("account_balance"),
        "created_at":      raw.get("created_at"),       # string, Postgres handles cast
    }


def upsert_customers(db: Session, customers: list[dict]) -> int:
    """
    Upsert customers into PostgreSQL.
    INSERT ... ON CONFLICT (customer_id) DO UPDATE
    """
    if not customers:
        return 0

    parsed = [parse_customer(c) for c in customers]

    stmt = insert(Customer).values(parsed)

    # On conflict (same customer_id), update all other fields
    stmt = stmt.on_conflict_do_update(
        index_elements=["customer_id"],
        set_={
            "first_name":      stmt.excluded.first_name,
            "last_name":       stmt.excluded.last_name,
            "email":           stmt.excluded.email,
            "phone":           stmt.excluded.phone,
            "address":         stmt.excluded.address,
            "date_of_birth":   stmt.excluded.date_of_birth,
            "account_balance": stmt.excluded.account_balance,
            "created_at":      stmt.excluded.created_at,
        }
    )

    db.execute(stmt)
    db.commit()

    return len(parsed)


def run_ingestion(db: Session) -> int:
    """Full ingestion pipeline: fetch from Flask → upsert to DB."""
    customers = fetch_all_customers_from_flask()
    records_processed = upsert_customers(db, customers)
    return records_processed