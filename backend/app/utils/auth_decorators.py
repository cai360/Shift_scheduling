from functools import wraps
from flask import request, jsonify, g
from app.services.auth_service import AuthService
from app.utils.response import ok, error


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return error("error: Missing or invalid token", 401, str(e))

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = AuthService.decode_token(token, expected_type="access")
        except Exception as e:
            return error("error: Missing or invalid token", 401, str(e))

        g.user_id = payload.get("sub")

        return fn(*args, **kwargs)
    return wrapper