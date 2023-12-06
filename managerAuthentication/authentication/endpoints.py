from typing import Annotated, Dict
from fastapi import APIRouter, Depends, Request
import requests

from authentication.user import loginUser, registerUser, getCurrentUser
from authentication.models import User
from authentication.jwt import JwtToken, refreshAccessToken
from manager.load_config import CONFIG

from fastapi import HTTPException, status

router = APIRouter()

@router.post("/login")
async def login(tokens: Annotated[Dict[str, JwtToken | User], Depends(loginUser)]) -> Dict[str, JwtToken | User]:
    return tokens

@router.post("/register")
async def register(success: Annotated[bool, Depends(registerUser)]):
    return {"status": success}

@router.get("/user")
async def getUser(user: Annotated[User, Depends(getCurrentUser)]) -> User:
    return user

@router.post("/refreshToken")
async def refreshToken(tokens: Annotated[Dict[str, JwtToken], Depends(refreshAccessToken)]) -> Dict[str, JwtToken]:
    return tokens

@router.get("/verify")
async def verify(user: Annotated[User, Depends(getCurrentUser)]) -> Dict:
    if user:
        return {"status": True}
    return {"status": False}

@router.post("/modUser")
async def modUser(request: Request, user: Annotated[User, Depends(getCurrentUser)]):
    resp = requests.get(CONFIG["PERSISTENCE_URL"]+"/persistence/queryElement/users", params={"username": user.username})

    
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = resp.json()["_id"]

    body = await request.json()
    mods = {}
    mod_list = ["username", "nombre", "cedula", "ubicacion", "password"]
    for k in mod_list:
        if k in body:
            mods[k] = body[k]

    resp = requests.post(CONFIG["PERSISTENCE_URL"]+"/persistence/modElement/users", params={"element_id": user_id}, json=mods)

    return {"status": resp.json()["status"]}
