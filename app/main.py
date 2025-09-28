# app/main.py
import json
import logging
import os
import sys
import time

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)

app = FastAPI(title="Starter FastAPI")

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"])

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(duration)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    logging.info("Root says OK")
    return {"message": "Hello from FastAPI!"}

@app.get("/healthz")
def healthz():
    logging.info("Health check OK")
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    logging.info("Ready check OK")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True}
    except SQLAlchemyError:
        return {"ready": False}
