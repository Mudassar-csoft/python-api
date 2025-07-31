# mylib/models.py   11
from pydantic import BaseModel
from typing import List,Optional

class DeviceConfig(BaseModel):
    campus_id: int
    ip: str
    port: int = 4370
    password: int = 0

class UserInfo(BaseModel):
    uid: int
    name: str
    user_id: str

class AttendanceLog(BaseModel):
    uid:str #uid for unique
    user_id: str
    timestamp: str
    status: int
    punch: int

class DeviceResponse(BaseModel):
    campus_id: int
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

class ZKUpdateUserIdRequest(BaseModel):
    campus_id: int
    old_user_id: str
    new_user_id: str
    name: Optional[str] = None
    privilege: Optional[int] = None


class ZKAddUserRequest(BaseModel):
    campus_id: int
    user_id: str
    name: str
    privilege: int = 0
    password: str = ''
    group_id: int = 1
    
class ZKDeleteUserRequest(BaseModel):
    campus_id: int
    user_id: str  # user_id in the machine

class MultiCampusRequest(BaseModel):
    campus_ids: List[int]