from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated, Optional

from mylib.core import greet
from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
from mylib.models import DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse

router = APIRouter()


# Dependency to get the application state
async def get_app_state(request: Request):
    return request.app.state


# Greet Endpoint
@router.get("/greet/{name}", tags=["Utility"])
async def greet_endpoint(name: str):
    return {"message": greet(name)}


# ZK Users Endpoint
@router.get("/zk/users", response_model=MultiZKUsersResponse, tags=["ZKTeco"])
async def get_zk_users_endpoint(
    ip: Annotated[str, Query(description="Device IP address")],
    port: Annotated[int, Query(description="Device port")],
    password: Annotated[int, Query(description="Device password")] = 0,
    uid: Annotated[Optional[int], Query(description="User UID filter")] = None,
    app_state=Depends(get_app_state)
):
    device_config = DeviceConfig(ip=ip, port=port, password=password)
    response = get_zk_users_from_devices([device_config])

    if uid is not None:
        for device in response.devices:
            device.users = [user for user in device.users if user.uid == uid]
            if not device.users:
                device.status = "error"
                device.message = f"No user found with UID {uid}"

    return response

# ZK Attendance Endpoint
@router.get("/zk/attendance", response_model=MultiZKAttendanceResponse, tags=["ZKTeco"])
async def get_zk_attendance_endpoint(
    ip: Annotated[str, Query(..., description="Device IP address")],
    port: Annotated[int, Query(..., description="Device port")],
    password: Annotated[int, Query(..., description="Device password")],
    app_state=Depends(get_app_state)
):
    device_config = DeviceConfig(ip=ip, port=port, password=password)
    return get_zk_attendance_from_devices([device_config])
