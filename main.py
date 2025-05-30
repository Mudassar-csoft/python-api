# main.py
from fastapi import FastAPI
from mylib.api.routes import router

app = FastAPI(title="My Python API")

app.include_router(router, prefix="/api/v1")