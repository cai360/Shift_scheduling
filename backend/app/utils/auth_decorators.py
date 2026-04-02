from functools import wraps
from flask import request, g
from app.services.auth_service import AuthService
from uuid import UUID
from werkzeug.exceptions import Unauthorized

import logging
logger = logging.getLogger(__name__)

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            logger.warning("JWT missing or invalid format: header=%s", auth_header)
            raise Unauthorized("Missing or invalid token")

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = AuthService.decode_token(token, expected_type="access")
            sub = payload.get("sub")
            if not sub:
                raise ValueError("Missing sub in token")
            g.user_id = UUID(sub)
        except Exception as e:
            logger.warning("JWT missing or invalid format")
            raise Unauthorized("Invalid or expired token")

        return fn(*args, **kwargs)
    return wrapper