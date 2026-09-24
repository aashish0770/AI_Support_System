# app/main.py
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limit import limiter

configure_logging()


app = FastAPI(title="AI Support System", version="1.0.0")
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/health")
def read_root():
    return {"status": "ok"}
