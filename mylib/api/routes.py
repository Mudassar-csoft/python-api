# mylib/api/routes.py
from fastapi import APIRouter
from mylib.core import greet
from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
from mylib.models import DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse
from typing import List

router = APIRouter()

@router.get("/greet/{name}")
async def greet_endpoint(name: str):
    return {"message": greet(name)}

@router.get("/zk/users", response_model=MultiZKUsersResponse)
async def get_zk_users_endpoint(ip: str, port: int = 4370, password: int = 0):
    device_config = DeviceConfig(ip=ip, port=port, password=password)
    return get_zk_users_from_devices([device_config])

@router.get("/zk/attendance", response_model=MultiZKAttendanceResponse)
async def get_zk_attendance_endpoint(ip: str, port: int = 4370, password: int = 0):
    device_config = DeviceConfig(ip=ip, port=port, password=password)
    return get_zk_attendance_from_devices([device_config])