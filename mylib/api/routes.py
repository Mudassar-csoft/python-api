from fastapi import APIRouter, Depends, Query, Request,HTTPException
from typing import Annotated, Optional
from mylib.core import greet
from zk import ZK
from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
from mylib.models import DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse, CampusRequest, ZKUpdateUserIdRequest,ZKAddUserRequest
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
    9: {"ip": "10.20.0.200", "port": 4369, "password": 1122},
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




@router.post("/zk/user/update-id", tags=["ZKTeco"])
async def update_user_id(payload: ZKUpdateUserIdRequest):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    try:
        zk = ZK(config['ip'], port=config['port'], timeout=5, password=config['password'], force_udp=False)
        conn = zk.connect()
        conn.disable_device()

        # Get existing users and find the one to update
        existing_users = conn.get_users()
        user_to_update = next((u for u in existing_users if str(u.user_id) == str(payload.old_user_id)), None)

        if not user_to_update:
            raise HTTPException(status_code=404, detail=f"User with user_id {payload.old_user_id} not found.")

        # Use fallback for optional fields
        updated_name = payload.name if payload.name is not None else user_to_update.name
        updated_privilege = payload.privilege if payload.privilege is not None else user_to_update.privilege

        conn.set_user(
            uid=user_to_update.uid,
            user_id=payload.new_user_id,
            name=updated_name,
            privilege=updated_privilege,
            password=user_to_update.password,
            group_id=user_to_update.group_id,
        )

        conn.enable_device()
        conn.disconnect()

        return {
            "status": "success",
            "message": f"user_id updated from {payload.old_user_id} to {payload.new_user_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zk/employees", tags=["ZKTeco"])
async def add_user_to_zk(payload: ZKAddUserRequest):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    try:
        zk = ZK(
            config["ip"],
            port=config["port"],
            timeout=5,
            password=config["password"],
            force_udp=False
        )
        conn = zk.connect()
        conn.disable_device()

        # Add user (no fingerprint yet)
        conn.set_user(
            uid=None,
            user_id=payload.user_id,
            name=payload.name,
            privilege=payload.privilege,
            password=payload.password,
            group_id=payload.group_id
        )

        conn.enable_device()
        conn.disconnect()

        return {
            "status": "success",
            "message": f"User '{payload.name}' (user_id={payload.user_id}) added successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZK Error: {str(e)}")
