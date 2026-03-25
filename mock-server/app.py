import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from schema.customer_schema import CustomerSchema
from schema.pagination import PaginationSchema, PaginatedResponseSchema
from auth.auth import require_token

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    return app


app = create_app()

# Load and validate all customers from JSON at startup
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "customers.json")

with open(DATA_FILE, "r") as f:
    raw = json.load(f)

# Validate every customer through Pydantic on load — fail fast if JSON is bad
CUSTOMERS = [CustomerSchema(**c) for c in raw]

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mock-server"})


@app.route("/api/customers", methods=["GET"])
@require_token
def get_customers():
    try:
        pagination = PaginationSchema(
            page=request.args.get("page", 1),
            limit=request.args.get("limit", 10)
        )
    except Exception as e:
        return jsonify({"error": "Invalid query params", "detail": str(e)}), 422

    start = (pagination.page - 1) * pagination.limit
    end   = start + pagination.limit
    paginated = CUSTOMERS[start:end]

    response = PaginatedResponseSchema(
        data=paginated,
        total=len(CUSTOMERS),
        page=pagination.page,
        limit=pagination.limit
    )

    return jsonify(response.model_dump(mode="json"))


@app.route("/api/customers/<customer_id>", methods=["GET"])
@require_token
def get_customer(customer_id):
    customer = next((c for c in CUSTOMERS if c.customer_id == customer_id), None)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({"data": customer.model_dump(mode="json")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)