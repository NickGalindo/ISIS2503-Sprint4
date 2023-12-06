from manager.load_config import CONFIG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from authentication import router as authentication_router

import colorama
from colorama import Fore


colorama.init(autoreset=True)

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

origins= ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication_router, prefix="/auth")

@app.get("/health")
def health():
    return {"status": "good"}
