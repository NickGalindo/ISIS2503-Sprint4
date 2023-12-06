from manager.load_config import CONFIG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import colorama

from encryption import router as encryption_router

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

app.include_router(encryption_router)
