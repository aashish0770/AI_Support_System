# app/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def read_root():
    return {"message": "Hello World"}
