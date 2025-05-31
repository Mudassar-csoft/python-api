# main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from fastapi import FastAPI
from mylib.api.routes import router

app = FastAPI(title="My Python API")

app.include_router(router, prefix="/api/v1")

# Use public IP directly
app.state.ngrok_host = "103.121.25.3"
app.state.ngrok_port = 4369

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)