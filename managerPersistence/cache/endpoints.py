from datetime import timedelta
from fastapi import APIRouter, Request

from cache import service

router = APIRouter()

@router.post("/checkBlacklist")
async def checkBlacklist(request: Request):
    body = await request.json()
    return {"status": service.checkJwtBlacklist(request.app.state.redisConnectionPool, body["token"])}

@router.post("/addBlacklist")
async def addBlacklist(request: Request):
    body = await request.json()
    return {"status": service.addJwtBlacklist(request.app.state.redisConnectionPool, body["token"], timedelta(weeks=1))}

@router.get("/checkUser")
async def checkUser(request: Request, username: str):
    usr = service.getUser(request.app.state.redisConnectionPool, username)

    if usr is None:
        return {"status": False}

    if usr["attempts"] >= 3:
        return {"status": True}

    return {"status": False}

@router.get("/addUserAttempt")
async def addUserAttempt(request: Request, username: str):
    usr = service.getUser(request.app.state.redisConnectionPool, username)

    if usr is None:
        service.setUser(request.app.state.redisConnectionPool, username, {"attempts": 1})
        return {"status": True}

    service.setUser(request.app.state.redisConnectionPool, username, {"attempts": usr["attempts"]+1})

    return {"status": True}
    
