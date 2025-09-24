# app/main.py
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import create_engine
import os

app = FastAPI(title="Starter FastAPI")
engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True}
    except SQLAlchemyError:
        return {"ready": False}
