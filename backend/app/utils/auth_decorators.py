from functools import wraps
from flask import request, g
from app.services.auth_service import AuthService

from functools import wraps
from flask import request, g
from app.services.auth_service import AuthService
import logging
logger = logging.getLogger(__name__)

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            logger.warning("JWT missing or invalid format: header=%s", auth_header)
            raise PermissionError("Missing or invalid token")

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = AuthService.decode_token(token, expected_type="access")
        except Exception as e:
            logger.warning("JWT decode failure: %s", e)
            raise PermissionError("Invalid or expired token")

        g.user_id = payload.get("sub")
        if not g.user_id:
            raise PermissionError("Invalid token payload")

        return fn(*args, **kwargs)
    return wrapper