from functools import wraps
from flask import request, jsonify, g
from app.services.auth_service import AuthService


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = AuthService.decode_token(token, "access")
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        g.user_id = int(payload.get("sub"))
        return fn(*args, **kwargs)

    return wrapper