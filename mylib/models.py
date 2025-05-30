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

class DeviceResponse(BaseModel):
    ip: str
    status: str
    message: str
    users: List[UserInfo]

class MultiZKUsersResponse(BaseModel):
    devices: List[DeviceResponse]