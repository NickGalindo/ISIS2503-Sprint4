from manager.load_config import CONFIG
from typing import Dict, Any

from datetime import datetime, timedelta

from typing import Annotated
from fastapi import Depends, Form, HTTPException, Request, status
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer

import jwt

import requests

# Class for a JWT token
class JwtToken(BaseModel):
    token: str
    token_type:str

# Extract username and password from Form()
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/login")
# Extract refresh token from Form()
async def extractRefreshToken(refresh_token: Annotated[str, Form()]) -> str:
    return refresh_token

async def createAccessToken(data: Dict, expires_delta: timedelta = timedelta(minutes=CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])):
    to_encode = data.copy()
    if "exp" in to_encode:
        del to_encode["exp"]

    res = requests.post(f"{CONFIG['ENCRYPTION_URL']}/encrypt", json=to_encode)
    to_encode = res.json()

    expire: datetime = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, CONFIG["ACCESS_SECRET_KEY"], algorithm=CONFIG["ENCRYPT_ALGORITHM"])

    return encoded_jwt

async def createRefreshToken(data: Dict, expires_delta: timedelta = timedelta(weeks=CONFIG["REFRESH_TOKEN_EXPIRE_WEEKS"])):
    to_encode = data.copy()
    if "exp" in to_encode:
        del to_encode["exp"]

    res = requests.post(f"{CONFIG['ENCRYPTION_URL']}/encrypt", json=to_encode)
    to_encode = res.json()

    expire: datetime = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, CONFIG["REFRESH_SECRET_KEY"], algorithm=CONFIG["ENCRYPT_ALGORITHM"])

    return encoded_jwt

async def decodeAccessToken(token: Annotated[str, Depends(OAUTH2_SCHEME)]) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        decoded_token = jwt.decode(token, CONFIG["ACCESS_SECRET_KEY"], algorithms=[CONFIG["ENCRYPT_ALGORITHM"]])
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    to_decode = decoded_token.copy()
    del to_decode["exp"]

    res = requests.post(f"{CONFIG['ENCRYPTION_URL']}/decrypt", json=to_decode)
    to_decode = res.json()

    to_decode["exp"] = decoded_token["exp"]

    return to_decode

async def decodeRefreshToken(refresh_token: str) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        decoded_token = jwt.decode(refresh_token, CONFIG["REFRESH_SECRET_KEY"], algorithms=[CONFIG["ENCRYPT_ALGORITHM"]])
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    to_decode = decoded_token.copy()
    del to_decode["exp"]

    res = requests.post(f"{CONFIG['ENCRYPTION_URL']}/decrypt", json=to_decode)
    to_decode = res.json()

    to_decode["exp"] = decoded_token["exp"]

    return to_decode

# Refresh Tokens
async def refreshAccessToken(token: Annotated[str, Depends(extractRefreshToken)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    resp = requests.post(CONFIG["PERSISTENCE_URL"]+"/cache/checkBlacklist", json={"token":token})
    if resp.json()["status"]:
        raise credentials_exception

    resp = requests.post(CONFIG["PERSISTENCE_URL"]+"/cache/addBlacklist", json={"token":token})
    if not resp.json()["status"]:
        raise credentials_exception

    data: Dict = await decodeRefreshToken(token)
    refresh_token = await createRefreshToken(data=data)
    data["sub"] = data["cedula"]
    access_token = await createAccessToken(data=data)

    return {"access_token": JwtToken(token=access_token, token_type="bearer"), "refresh_token": JwtToken(token=refresh_token, token_type="bearer")}
