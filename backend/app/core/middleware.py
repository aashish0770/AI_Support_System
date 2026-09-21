# backend/app/core/middleware.py

from __future__ import annotations

import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8] # 8 char uuid, cut short for development
        token = request_id_var.set(request_id)
        start = time.monotonic()

        try:
            logger.info(f"{request.method} {request.url.path} - started")
            response = await call_next(request)
            duration_ms = (time.monotonic() - start) * 1000
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} ({duration_ms:.0f}ms)"
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception:
            logger.exception(f"{request.method} {request.url.path} - request failed")
            raise

        finally:
            request_id_var.reset(token)
