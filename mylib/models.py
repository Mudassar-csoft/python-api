# mylib/models.py
from pydantic import BaseModel, IPvAnyAddress
from typing import List

class DeviceConfig(BaseModel):
    ip: IPvAnyAddress
    port: int = 4370
    password: int = 0

class UserInfo(BaseModel):
    uid: int
    name: str
    user_id: str

class AttendanceLog(BaseModel):
    user_id: str
    timestamp: str  # ISO format string (e.g., "2025-05-30T19:46:00")
    status: int
    punch: int

class DeviceResponse(BaseModel):
    ip: str
    status: str
    message: str
    users: List[UserInfo] = []
    attendances: List[AttendanceLog] = []

class MultiZKUsersResponse(BaseModel):
    devices: List[DeviceResponse]

class MultiZKAttendanceResponse(BaseModel):
    devices: List[DeviceResponse]