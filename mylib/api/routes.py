# mylib/api/routes.py
from fastapi import APIRouter, Depends, Request
from mylib.core import greet
# from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
# from mylib.models import DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse
# from typing import List

router = APIRouter()

async def get_app_state(request: Request):
    return request.app.state

@router.get("/greet/{name}")
async def greet_endpoint(name: str):
    return {"message": greet(name)}

# @router.get("/zk/users", response_model=MultiZKUsersResponse)
# async def get_zk_users_endpoint(
#     ip: str = "103.121.25.3",
#     port: int = 4369,
#     password: int = 1122,
#     app_state=Depends(get_app_state)
# ):
#     # Use ngrok host/port if ip matches the device IP
#     if ip in ["103.121.25.3", "103.121.25.6"]:
#         ngrok_host = app_state.ngrok_host
#         ngrok_port = app_state.ngrok_port
#         device_config = DeviceConfig(ip=ngrok_host, port=ngrok_port, password=password)
#     else:
#         device_config = DeviceConfig(ip=ip, port=port, password=password)
#     return get_zk_users_from_devices([device_config])

# @router.get("/zk/attendance", response_model=MultiZKAttendanceResponse)
# async def get_zk_attendance_endpoint(
#     ip: str = "103.121.25.3",
#     port: int = 4369,
#     password: int = 1122,
#     app_state=Depends(get_app_state)
# ):
#     if ip in ["103.121.25.3", "103.121.25.6"]:
#         ngrok_host = app_state.ngrok_host
#         ngrok_port = app_state.ngrok_port
#         device_config = DeviceConfig(ip=ngrok_host, port=ngrok_port, password=password)
#     else:
#         device_config = DeviceConfig(ip=ip, port=port, password=password)
#     return get_zk_attendance_from_devices([device_config])