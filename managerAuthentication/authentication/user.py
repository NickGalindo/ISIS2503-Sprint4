from manager.load_config import CONFIG

from typing import Annotated, Dict

from colorama import Fore

from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from passlib.context import CryptContext

from authentication.jwt import JwtToken, createAccessToken, decodeAccessToken, createRefreshToken

from mysql.connector.pooling import MySQLConnectionPool

from authentication.models import User

import requests

# Hashing
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def __verifyPassword(password: str, db_password: str):
    return PWD_CONTEXT.verify(password, db_password)

def __hashPassword(password: str):
    return PWD_CONTEXT.hash(password)


# database interaction
async def __authenticate(username: str, password: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    resp = requests.get(CONFIG["PERSISTENCE_URL"]+"/persistence/queryElement/users", params={"username":username})
    if resp.status_code != 200:
        raise credentials_exception
    
    resp = resp.json()

    db_password = resp["password"]

    if not __verifyPassword(password, db_password):
        resp = requests.get(CONFIG["PERSISTENCE_URL"]+"/cache/addUserAttempt", params={"username":username})
        print(resp)
        raise credentials_exception

    usr = User(
        username=resp["username"],
        nombre=resp["nombre"],
        cedula=resp["cedula"],
        ubicacion=resp["ubicacion"]
    )

    return usr

async def __register(usr: User, password: str) -> bool:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    resp = requests.post(CONFIG["PERSISTENCE_URL"]+"/persistence/addElement/users", json={
        "username": usr.username,
        "nombre": usr.nombre,
        "cedula": usr.cedula,
        "ubicacion": usr.ubicacion,
        "password": __hashPassword(password)
    })

    if resp.status_code != 200:
        raise credentials_exception

    return resp.json()["status"]


# user functions
async def getCurrentUser(decoded_token: Annotated[Dict, Depends(decodeAccessToken)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not decoded_token.get("sub"):
        raise credentials_exception

    try:
        user = User(
            username=decoded_token["username"],
            nombre=decoded_token["nombre"],
            cedula=decoded_token["cedula"],
            ubicacion=decoded_token["ubicacion"]
        )
    except KeyError:
        raise credentials_exception

    return user

async def loginUser(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Dict[str, JwtToken | User]:
    resp = requests.get(CONFIG["PERSISTENCE_URL"]+"/cache/checkUser", params={"username":form_data.username})
    print(resp)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    print(resp.json())

    if resp.json()["status"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Due to failed attempts your user has been blocked",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = await __authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = await createAccessToken(
        data={
            "username": user.username,
            "nombre": user.nombre,
            "cedula": user.cedula,
            "ubicacion": user.ubicacion,
            "sub": user.cedula
        }
    )

    refresh_token = await createRefreshToken(
        data={
            "username": user.username,
            "nombre": user.nombre,
            "cedula": user.cedula,
            "ubicacion": user.ubicacion,
        }
    )

    return {"access_token": JwtToken(token=access_token, token_type="bearer"), "refresh_token": JwtToken(token=refresh_token, token_type="bearer"), "User": user}

async def registerUser(request: Request, username: Annotated[str, Form()], nombre: Annotated[str, Form()], cedula: Annotated[str, Form()], ubicacion: Annotated[str, Form()], password: Annotated[str, Form()]):
    usr = User(
        username=username,
        nombre=nombre,
        cedula=cedula,
        ubicacion=ubicacion
    )

    return await __register(usr, password)
