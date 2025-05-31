# mylib/api/routes.py (Vercel version)
from fastapi import APIRouter
from mylib.core import greet

router = APIRouter()

@router.get("/greet/{name}")
async def greet_endpoint(name: str):
    return {"message": greet(name)}