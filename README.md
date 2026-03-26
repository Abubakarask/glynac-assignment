# Glynac Customer Data Pipeline

A containerised 3-service data pipeline built with Flask, FastAPI, and PostgreSQL.

## Architecture
```
customers.json → Flask Mock Server (5000) → FastAPI Pipeline (8000) → PostgreSQL (5432)
```

- **Flask** — Mock server that reads customer data from a JSON file and serves it via REST
- **FastAPI** — Pipeline service that ingests from Flask, stores in PostgreSQL, and serves data
- **PostgreSQL** — Persistent data storage with upsert support

## Project Structure
```
glynac-assignment/
├── docker-compose.yml
├── .gitignore
├── mock-server/
│   ├── app.py                   # Flask app — 3 endpoints + bearer token auth
│   ├── auth/
│   │   └── auth.py              # require_token decorator
│   ├── schema/
│   │   ├── customer_schema.py   # CustomerSchema (Pydantic)
│   │   └── pagination.py        # PaginationSchema, PaginatedResponseSchema
│   ├── data/
│   │   └── customers.json       # 22 mock customers
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
└── pipeline-service/
    ├── main.py                  # FastAPI app — 3 endpoints + health
    ├── database.py              # SQLAlchemy engine + session
    ├── models/
    │   └── customer.py          # Customer DB model
    ├── schemas/
    │   ├── customer.py          # CustomerResponse, PaginatedCustomerResponse
    │   ├── ingeston.py          # IngestResponse
    │   └── general.py          # HealthResponse, PaginationResponse
    ├── services/
    │   └── ingestion.py         # Fetch from Flask + upsert to PostgreSQL
    ├── Dockerfile
    ├── requirements.txt
    └── .env.example
```

## Prerequisites

- Docker Desktop (running)
- Git

## Environment Setup

Copy the example files and fill in your own values:
```bash
cp mock-server/.env.example mock-server/.env
cp pipeline-service/.env.example pipeline-service/.env
```


## Running the Project
```bash
# Clone the repo
git clone https://github.com/Abubakarask/glynac-assignment.git
cd glynac-assignment

# Start all 3 services
docker-compose up --build -d

# Verify all containers are running
docker-compose ps
```

## API Reference

### Flask Mock Server — `http://localhost:5000`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | None | Health check |
| GET | `/api/customers` | Bearer token | Paginated customer list |
| GET | `/api/customers/{id}` | Bearer token | Single customer |

### FastAPI Pipeline Service — `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/ingest` | Fetch from Flask → upsert to PostgreSQL |
| GET | `/api/customers` | Paginated customers from DB |
| GET | `/api/customers/{id}` | Single customer from DB |

## Testing

**PowerShell (Windows)**
```powershell
# Health checks
curl http://localhost:5000/api/health
curl http://localhost:8000/api/health

# Flask — without token (expect 401)
curl http://localhost:5000/api/customers

# Flask — with token
curl http://localhost:5000/api/customers `
  -Headers @{ Authorization = "Bearer {EXCHANGE_TOKEN}" }

# Trigger ingestion
curl -Method POST http://localhost:8000/api/ingest

# Get customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Single customer
curl http://localhost:8000/api/customers/CUST001
```

**Git Bash / Linux / Mac**
```bash
# Flask with token
curl http://localhost:5000/api/customers \
  -H "Authorization: Bearer {EXCHANGE_TOKEN}"

# Trigger ingestion
curl -X POST http://localhost:8000/api/ingest

# Get customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"
```

## Key Implementation Details

**Bearer Token Auth** — All Flask customer endpoints require an `Authorization: Bearer <token>` header matching `EXCHANGE_TOKEN` in `.env`. Returns 401 if missing, 403 if wrong.

**Pydantic Validation** — Customers are validated at startup when loaded from JSON. Invalid data fails immediately rather than at request time.

**Auto-pagination Ingestion** — The ingest endpoint automatically handles Flask's pagination, fetching all pages until complete.

**Upsert Logic** — Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` so running ingest multiple times never creates duplicates.

**Persistent Storage** — PostgreSQL data is stored in a named Docker volume (`pgdata`) so data survives container restarts.

## Stopping Services
```bash
# Stop containers
docker-compose down

# Stop and wipe database
docker-compose down -v
```