import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

class AuthService:
    @staticmethod
    def _cfg(name: str, default=None):
        val = current_app.config.get(name)
        if val is not None: 
            return val
        return os.getenv(name, default)
    
    @staticmethod
    def hash_password(plain: str) -> str:
        if not isinstance(plain, str) or len(plain) < 8:
            raise ValueError("Password too short")
        # bcrypt.hashpw(密碼bytes, salt)
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
        

    @staticmethod
    def issue_tokens(user_id: int) -> dict:
        secret = AuthService._cfg("JWT_SECRET")
        if not secret:
            raise RuntimeError("JWT_SECRET not configured"
            )
        access_minutes = int(AuthService._cfg("JWT_ACCESS_EXPIRES_MINUTES", 15))
        refresh_days = int(AuthService._cfg("JWT_REFRESH_EXPIRES_DAYS", 7))
        now = datetime.now(timezone.utc)

        #access token (subject, type, issued_at, expired)
        a = {
            "sub": str(user_id),
            "type": "access",
            "iat" : int(now.timestamp()),
            "exp" : int((now + timedelta(minutes=access_minutes)).timestamp()) 
        }

        r = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=refresh_days)).timestamp())
        }

        return {
            "access_token": jwt.encode(a, secret, algorithm="HS256"),
            "refresh_token": jwt.encode(r, secret, algorithm="HS256"),
        }
    

@staticmethod
def decode_token(token: str, expected_type: str) -> dict:
    secret = AuthService._cfg("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET not configured")
    try: 
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalid")

@staticmethod
def issue_access_from_refresh(refresh_token: str) -> dict:
    payload = AuthService.decode_token(refresh_token, "refresh")
    user_id = int(payload["sub"])
    secret = AuthService._cfg("JWT_SECRET")

    now = datetime.now(timezone.utc)
    access_minutes = int(AuthService._cfg("JWT_ACCESS_EXPIRES_MINUTES", 15))
    a = {
        "sub" : str(user_id),
        "type": "access",
        "iat" : int(now.timestamp()),
        "exp" : int((now + timedelta(minutes=access_minutes)).timestamp())
    }

    return {"access_token": jwt.encode(a, secret, algorithm="HS256")}



    







    
        