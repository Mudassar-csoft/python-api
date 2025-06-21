# mylib/zk_device.py
from zk import ZK, const
from .models import DeviceConfig, DeviceResponse, UserInfo, MultiZKUsersResponse, AttendanceLog, MultiZKAttendanceResponse
from typing import List
import socket
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_device(config: DeviceConfig):
    zk = ZK(
        ip=str(config.ip),
        port=config.port,
        timeout=3,
        password=config.password,
        force_udp=False,
        ommit_ping=False
    )
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(3)
    try:
        conn = zk.connect()
        socket.setdefaulttimeout(old_timeout)
        return conn
    except Exception as e:
        socket.setdefaulttimeout(old_timeout)
        raise e

def get_zk_users_from_devices(device_configs: List[DeviceConfig]) -> MultiZKUsersResponse:
    results = []
    for config in device_configs:
        conn = None
        device_result = DeviceResponse(campus_id=config.campus_id, status="error", message="", users=[], attendances=[])
        try:
            logger.info(f"Connecting to {config.ip}:{config.port}")
            conn = connect_to_device(config)
            logger.info(f"Connected to {config.ip}")
            conn.disable_device()
            users = conn.get_users()
            device_result.users = [
                UserInfo(uid=user.uid, name=user.name, user_id=user.user_id)
                for user in users
            ]
            device_result.status = "success"
            device_result.message = f"Users retrieved successfully from {config.campus_id}"
        except Exception as e:
            logger.error(f"Error connecting to {config.ip}: {str(e)}")
            device_result.message = f"Error connecting to {config.ip}: {str(e)}"
        finally:
            if conn:
                conn.enable_device()
                conn.disconnect()
            logger.info(f"Disconnected from {config.ip}")
        results.append(device_result)
    return MultiZKUsersResponse(devices=results)

def get_zk_attendance_from_devices(device_configs: List[DeviceConfig]) -> MultiZKAttendanceResponse:
    results = []
    for config in device_configs:
        conn = None
        device_result = DeviceResponse(campus_id=config.campus_id, status="error", message="", users=[], attendances=[])
        try:
            logger.info(f"Connecting to {config.ip}:{config.port} for attendance")
            conn = connect_to_device(config)
            logger.info(f"Connected to {config.ip}")
            conn.disable_device()
            attendances = conn.get_attendance()
            device_result.attendances = [
                AttendanceLog(
                    user_id=attendance.user_id,
                    timestamp=attendance.timestamp.isoformat(),
                    status=attendance.status,
                    punch=attendance.punch
                )
                for attendance in attendances
            ]
            device_result.status = "success"
            device_result.message = f"Attendance retrieved successfully from {config.campus_id}"
        except Exception as e:
            logger.error(f"Error connecting to {config.ip}: {str(e)}")
            device_result.message = f"Error connecting to {config.ip}: {str(e)}"
        finally:
            if conn:
                conn.enable_device()
                conn.disconnect()
            logger.info(f"Disconnected from {config.ip}")
        results.append(device_result)
    return MultiZKAttendanceResponse(devices=results)