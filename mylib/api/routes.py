from fastapi import APIRouter, Depends, Query, Request,HTTPException
from typing import Annotated, Optional

from mylib.core import greet
from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
from mylib.models import DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse, CampusRequest
router = APIRouter()


# Dependency to get the application state
async def get_app_state(request: Request):
    return request.app.state


# Greet Endpoint
@router.get("/greet/{name}", tags=["Utility"])
async def greet_endpoint(name: str):
    return {"message": greet(name)}


# ZK Users Endpoint


# Secure campus config mapping
DEVICE_CONFIG = {
    9: {"ip": "103.121.25.3", "port": 4369, "password": 1122},
    7: {"ip": "103.121.25.6", "port": 4369, "password": 1122},
    8: {"ip": "103.121.25.4", "port": 4369, "password": 1122},
    20: {"ip": "101.53.242.96", "port": 4369, "password": 1122},
    
}

@router.post("/zk/users", response_model=MultiZKUsersResponse, tags=["ZKTeco"])
async def get_zk_users_by_campus(
    payload: CampusRequest,
    app_state=Depends(get_app_state)
):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    device_config = DeviceConfig(**config)
    response = get_zk_users_from_devices([device_config])
    return response


# ZK Attendance Endpoint
@router.post("/zk/attendance", response_model=MultiZKAttendanceResponse, tags=["ZKTeco"])
async def get_zk_attendance_by_campus(
    payload: CampusRequest,
    app_state=Depends(get_app_state)
):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    device_config = DeviceConfig(**config)
    response = get_zk_attendance_from_devices([device_config])
    return response
