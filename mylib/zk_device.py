# mylib/zk_device.py
from zk import ZK, const
from .models import DeviceConfig, DeviceResponse, UserInfo, MultiZKUsersResponse
from typing import List
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_zk_users_from_devices(device_configs: List[DeviceConfig]) -> MultiZKUsersResponse:
    results = []
    for config in device_configs:
        conn = None
        device_result = DeviceResponse(ip=str(config.ip), status="error", message="", users=[])
        try:
            logger.info(f"Connecting to {config.ip}:{config.port}")
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
            conn = zk.connect()
            socket.setdefaulttimeout(old_timeout)
            logger.info(f"Connected to {config.ip}")
            conn.disable_device()
            users = conn.get_users()
            device_result.users = [
                UserInfo(uid=user.uid, name=user.name, user_id=user.user_id)
                for user in users
            ]
            device_result.status = "success"
            device_result.message = f"Users retrieved successfully from {config.ip}"
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