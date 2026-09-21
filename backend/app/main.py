# app/main.py
from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

configure_logging()


app = FastAPI(title="AI Support System", version="1.0.0")
app.add_middleware(RequestIDMiddleware)

app.include_router(chat_router)


@app.get("/health")
def read_root():
    return {"message": "Hello World"}
