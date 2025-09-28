# app/main.py
import json
import logging
import os
import sys

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError


# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Apply formatter to root logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
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
