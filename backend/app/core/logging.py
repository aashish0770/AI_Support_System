# backend/app/core/logging.py

from __future__ import annotations

import sys
from contextvars import ContextVar

from loguru import logger

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def configure_logging() -> None:
    logger.remove()

    def _inject_request_id(record):
        record["extra"]["request_id"] = request_id_var.get()

    logger.configure(patcher=_inject_request_id)
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | req={extra[request_id]} | {message}",
        level="INFO",
    )
