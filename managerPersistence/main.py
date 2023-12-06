from manager.load_config import CONFIG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import redis

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import colorama
from colorama import Fore

from persistence.endpoints import router as persistence_router
from cache.endpoints import router as cache_router

colorama.init(autoreset=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.pymongoConnection = MongoClient(f"mongodb+srv://{CONFIG['MONGO_USER']}:{CONFIG['MONGO_PASSWORD']}@isis2503-sprint4.xzevczy.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
        print(Fore.GREEN + "SUCCESS: Connection with MongoAtlas established")
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't connect with MongoAtlas")

    try:
        app.state.pymongoConnection.admin.command('ping')
        print(Fore.GREEN+"SUCCESS: Succesfully pinged MongoAtlas cluster")
    except Exception as e:
        print(Fore.RED+"ERROR: Failed to ping MongoAtlas Cluster")

    try:
        app.state.redisConnectionPool = redis.ConnectionPool(
            host=CONFIG["REDIS_HOST"],
            port=CONFIG["REDIS_PORT"],
            decode_responses=True
        )
        print(Fore.GREEN+"SUCCESS: Succesfully connected to redis")
    except Exception as e:
        print(Fore.RED + "ERROR: connection to redis cache failed")
        raise e

    yield

    app.state.pymongoConnection.close()
    app.state.redisConnectionPool.disconnect()

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None, lifespan=lifespan)

origins= ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(persistence_router, prefix="/persistence")
app.include_router(cache_router, prefix="/cache")
