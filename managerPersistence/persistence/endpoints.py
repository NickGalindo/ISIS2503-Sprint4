from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import Receive

from persistence import service

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="verify")

router = APIRouter()

@router.post("/addElement/{collection}")
async def addElement(request: Request, collection: str):
    body = await request.json()
    body["version"] = 1

    return {"status": service.addElement(request.app.state.pymongoConnection, collection, body)}

@router.post("/modElement/{collection}")
async def modElement(request: Request, collection: str, element_id: str):
    body = await request.json()

    curElement = service.getElement(request.app.state.pymongoConnection, collection, element_id)

    if not curElement:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document doesn't exit",
            headers={"WWW-Authenticate": "Bearer"}
        )

    for k in curElement:
        if k in body:
            if k == "version":
                continue
            if k == "username":
                continue
            curElement[k] = body[k]
    curElement["version"] = curElement["version"]+1
    del curElement["_id"]

    return {"status": service.addElement(request.app.state.pymongoConnection, collection, curElement)}

@router.get("/getElement/{collection}")
async def getElement(request: Request, collection: str, element_id: str):
    elem = service.getElement(request.app.state.pymongoConnection, collection, element_id)

    if not elem:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document",
            headers={"WWW-Authenticate": "Bearer"}
        )

    elem["_id"] = str(elem["_id"])

    return elem


@router.get("/delElement/{collection}")
async def delElement(request: Request, collection: str, element_id: str):
    res = service.delElement(request.app.state.pymongoConnection, collection, element_id)

    if not res:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"message": "sucessfully deleted element"}

@router.get("/queryElement/{collection}")
async def queryElement(request: Request, collection: str, username: str):
    res = service.queryElement(request.app.state.pymongoConnection, collection, username)

    if not res:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error finding document",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    res["_id"] = str(res["_id"])

    return res

