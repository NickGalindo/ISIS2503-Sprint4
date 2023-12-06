from typing import Annotated, Dict
from fastapi import APIRouter, Request

from encryption import service

router = APIRouter()

@router.post("/encrypt")
async def encrypt(request: Request) -> Dict:
    payload = await request.json()

    return service.encrypt(payload)

@router.post("/decrypt")
async def decrypt(request: Request) -> Dict:
    payload = await request.json()

    return service.decrypt(payload)
