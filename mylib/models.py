# mylib/models.py
from pydantic import BaseModel
from typing import List

class DeviceConfig(BaseModel):
    ip: str
    port: int = 4370
    password: int = 0

class UserInfo(BaseModel):
    uid: int
    name: str
    user_id: str

class AttendanceLog(BaseModel):
    user_id: str
    timestamp: str
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

class CampusRequest(BaseModel):
    campus_id: int