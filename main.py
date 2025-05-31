# main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from fastapi import FastAPI
from mylib.api.routes import router
from pyngrok import ngrok
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="My Python API")

app.include_router(router, prefix="/api/v1")

# # ngrok setup
# NGROK_AUTH_TOKEN = "2xoyTAdgPTm2K6D3qjMNeFFASTz_3qGABgJP1KxTTHbTNxggy"
# ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# # Start ngrok tunnel to expose ZKTeco device
# try:
#     tunnel = ngrok.connect(4370, "tcp")  # Removed bind_tls, as it's not applicable for TCP
#     public_url = tunnel.public_url
#     logger.info(f"ngrok tunnel established: {public_url}")
#     # Extract host and port from ngrok URL (e.g., tcp://0.tcp.ngrok.io:12345)
#     ngrok_host = public_url.split("//")[1].split(":")[0]  # e.g., 0.tcp.ngrok.io
#     ngrok_port = int(public_url.split(":")[-1])  # e.g., 12345
# except Exception as e:
#     logger.error(f"Failed to establish ngrok tunnel: {str(e)}")
#     ngrok_host, ngrok_port = "103.121.25.3", 4369  # Fallback to public IP and external port

# # Store ngrok host and port in app state
# app.state.ngrok_host = ngrok_host
# app.state.ngrok_port = ngrok_port

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)