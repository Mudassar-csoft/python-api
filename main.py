# main.py
from fastapi import FastAPI
from mylib.api.routes import router

app = FastAPI(title="My Python API")

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)