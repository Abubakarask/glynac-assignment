import os
from functools import wraps
from flask import jsonify, request

# ─── Auth Decorator ───────────────────────────────────────────────────────────

def require_token(f):
    """
    Checks Authorization header for a valid Bearer token.
    Token must match EXCHANGE_TOKEN in .env
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        expected_token = os.getenv("EXCHANGE_TOKEN")

        if not expected_token:
            return jsonify({"error": "Server misconfiguration: EXCHANGE_TOKEN not set"}), 500

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        provided_token = auth_header.split("Bearer ")[1].strip()

        if provided_token != expected_token:
            return jsonify({"error": "Invalid token"}), 403

        return f(*args, **kwargs)
    return decorated

