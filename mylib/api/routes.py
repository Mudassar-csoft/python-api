from fastapi import APIRouter, Depends, HTTPException, Request
from mylib.core import greet
from mylib.security import verify_api_key
from zk import ZK
from mylib.zk_device import get_zk_users_from_devices, get_zk_attendance_from_devices
from mylib.models import (
    DeviceConfig, MultiZKUsersResponse, MultiZKAttendanceResponse,
    CampusRequest, ZKUpdateUserIdRequest, ZKAddUserRequest, ZKDeleteUserRequest,MultiCampusRequest
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Secure campus config mapping
DEVICE_CONFIG = {
    9:  {"ip": "101.53.242.172","port":4369,"password":1122},
    7:  {"ip": "101.53.242.173","port": 4369, "password": 1122},
    8:  {"ip": "101.53.242.171", "port": 4369, "password": 1122},
    20: {"ip": "101.53.242.96", "port": 4369, "password": 1122},
    12: {"ip": "182.186.104.150", "port": 4369, "password": 1122},
}


# Utility function to get device config
def get_device_config(campus_id: int) -> DeviceConfig:
    config = DEVICE_CONFIG.get(campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")
    return DeviceConfig(**config)


# Dependency to get application state
async def get_app_state(request: Request):
    return request.app.state


# Greeting endpoint
@router.get("/greet/{name}", tags=["Utility"])
async def greet_endpoint(name: str):
    return {"message": greet(name)}


# Fetch users from specific campus
@router.post("/zk/users", response_model=MultiZKUsersResponse, tags=["ZKTeco"])
async def get_zk_users_by_campus(
    payload: CampusRequest,
    _=Depends(verify_api_key)
):
    device_config = get_device_config(payload.campus_id)
    return get_zk_users_from_devices([device_config])


# Fetch attendance from specific campus
@router.post("/zk/attendance", response_model=MultiZKAttendanceResponse, tags=["ZKTeco"])
async def get_zk_attendance_by_campus(
    payload: CampusRequest,
    _=Depends(verify_api_key)
):
    device_config = get_device_config(payload.campus_id)
    return get_zk_attendance_from_devices([device_config])


# Update user ID on device
@router.post("/zk/user/update-id", tags=["ZKTeco"])
async def update_user_id(payload: ZKUpdateUserIdRequest, _=Depends(verify_api_key)):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    try:
        zk = ZK(config['ip'], port=config['port'], timeout=5, password=config['password'], force_udp=False)
        conn = zk.connect()
        conn.disable_device()

        existing_users = conn.get_users()
        user_to_update = next((u for u in existing_users if str(u.user_id) == str(payload.old_user_id)), None)
        if not user_to_update:
            raise HTTPException(status_code=404, detail=f"User with user_id {payload.old_user_id} not found.")

        conn.set_user(
            uid=user_to_update.uid,
            user_id=payload.new_user_id,
            name=payload.name or user_to_update.name,
            privilege=payload.privilege if payload.privilege is not None else user_to_update.privilege,
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
        logger.exception("User ID update failed")
        raise HTTPException(status_code=500, detail=str(e))


# Add new user to device
@router.post("/zk/employees", tags=["ZKTeco"])
async def add_user_to_zk(payload: ZKAddUserRequest, _=Depends(verify_api_key)):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Invalid campus_id: {payload.campus_id}")

    logger.info(f"Config for campus_id {payload.campus_id}: {config}")  # Debug log

    try:
        zk = ZK(config["ip"], port=config["port"], timeout=5, password=config["password"], force_udp=False)
        conn = zk.connect()
        logger.info("Device connected successfully")  # Debug log
        conn.disable_device()

        conn.set_user(
            uid=None,
            user_id=str(payload.user_id),
            name=payload.name,
            privilege=payload.privilege,
            password=payload.password,
            group_id=str(payload.group_id)
        )

        conn.enable_device()
        conn.disconnect()

        return {
            "status": "success",
            "message": f"User '{payload.name}' (user_id={payload.user_id}) added successfully."
        }

    except Exception as e:
        logger.exception("Add user failed")
        raise HTTPException(status_code=500, detail=f"ZK Error: {str(e)}")
            
# Fetch all users from all devices
@router.get("/zk/all-users", response_model=MultiZKUsersResponse, tags=["ZKTeco"])
async def get_all_zk_users(_=Depends(verify_api_key)):
    device_list = [
        DeviceConfig(campus_id=campus_id, **cfg)
        for campus_id, cfg in DEVICE_CONFIG.items()
    ]
    return get_zk_users_from_devices(device_list)


# Fetch all attendance from all devices
@router.get("/zk/all-attendance", response_model=MultiZKAttendanceResponse, tags=["ZKTeco"])
async def get_all_zk_attendance(_=Depends(verify_api_key)):
    device_list = [
        DeviceConfig(campus_id=campus_id, **cfg)
        for campus_id, cfg in DEVICE_CONFIG.items()
    ]
    return get_zk_attendance_from_devices(device_list)



# Optional: Check device status
@router.get("/zk/status", tags=["ZKTeco"])
async def check_device_status(campus_id: int, _=Depends(verify_api_key)):
    try:
        device_config = get_device_config(campus_id)
        zk = ZK(device_config.ip, port=device_config.port, timeout=3, password=device_config.password)
        conn = zk.connect()
        conn.disconnect()
        return {"status": "online", "message": f"Device at {device_config.ip} is reachable"}
    except Exception as e:
        logger.warning(f"Device at campus {campus_id} is offline: {e}")
        return {"status": "offline", "message": str(e)}
    
    
   

@router.post("/zk/delete-user", tags=["ZKTeco"])
async def delete_zk_user(payload: ZKDeleteUserRequest, _=Depends(verify_api_key)):
    config = DEVICE_CONFIG.get(payload.campus_id)
    if not config:
        raise HTTPException(status_code=404, detail="Invalid campus_id")

    logger.info(f"Attempting to connect to {config['ip']}:{config['port']} with password {config['password']}")

    try:
        zk = ZK(
            config['ip'],
            port=config['port'],
            timeout=20,  # Increased to 20 seconds
            password=config['password'],
            force_udp=False  # Using TCP
        )
        logger.info(f"Initializing connection to {config['ip']}:{config['port']}")
        conn = zk.connect()
        logger.info("Device connected successfully")
        conn.disable_device()

        logger.info("Fetching users from device")
        users = conn.get_users()
        logger.info(f"Found {len(users)} users. Searching for user_id: {payload.user_id}")
        target = next((u for u in users if str(u.user_id) == payload.user_id), None)  # Direct string comparison

        if not target:
            conn.enable_device()
            conn.disconnect()
            raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

        logger.info(f"Deleting user with UID {target.uid} and user_id {target.user_id}")
        conn.delete_user(uid=target.uid)
        logger.info(f"User {payload.user_id} deleted successfully")
        conn.enable_device()
        conn.disconnect()

        return {"status": "success", "message": f"User {payload.user_id} deleted from ZKTeco device"}

    except Exception as e:
        logger.exception("Delete user failed")
        raise HTTPException(status_code=500, detail=f"ZK Error: {str(e)}")
      
@router.post("/zk/devices-status", tags=["ZKTeco"])
async def check_multiple_zkteco_devices(payload: MultiCampusRequest,  _=Depends(verify_api_key)):
    results = []

    for campus_id in payload.campus_ids:
        config = DEVICE_CONFIG.get(campus_id)

        if not config:
            results.append({
                "campus_id": campus_id,
                "status": "not_configured",
                "message": "No device configuration found."
            })
            continue

        ip = config["ip"]
        port = config.get("port", 4370)
        password = config.get("password", 0)

        zk = ZK(ip, port=port, password=password, timeout=3)
        try:
            conn = zk.connect()
            conn.disconnect()
            results.append({
                "campus_id": campus_id,
                "ip": ip,
                "status": "online",
                "message": "ZKTeco device is online."
            })
        except Exception as e:
            results.append({
                "campus_id": campus_id,
                "ip": ip,
                "status": "offline",
                "message": str(e)
            })

    return {"devices": results}