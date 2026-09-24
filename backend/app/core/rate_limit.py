# backend/app/core/rate_limit.py

from __future__ import annotations

from fastapi import Request
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.security import decode_token


def rate_limit_key(request: Request) -> str:
    """per user limiting when authenticated, per IP when not authenticated"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ")
        try:
            payload = decode_token(token)
            if payload.get("type") == "access":
                return f"user:{payload['sub']}"
        except JWTError:
            pass
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=rate_limit_key,
    storage_uri=get_settings().redis_url,
    headers_enabled=True,  # this is what adds retry-after
)
