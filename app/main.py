# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Starter FastAPI")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"status": "ok"}
