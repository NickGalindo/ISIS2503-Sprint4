from typing import Dict
from bson import ObjectId
from fastapi import HTTPException
import pymongo
from pymongo.mongo_client import MongoClient
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

def addElement(mongoConnection: MongoClient, collection: str, element: Dict) -> bool:
    db = mongoConnection["ISIS2503-Sprint4"]
    col = db[collection]
    
    res = col.insert_one(element)

    return True

def getElement(mongoConnection: MongoClient, collection: str, element_id: str) -> Dict | None:
    db = mongoConnection["ISIS2503-Sprint4"]
    col = db[collection]

    res = col.find_one({"_id": ObjectId(element_id)})

    return res

def delElement(mongoConnection: MongoClient, collection: str, element_id: str) -> bool:
    db = mongoConnection["ISIS2503-Sprint4"]
    col = db[collection]

    res = col.delete_one({"_id": ObjectId(element_id)})

    if res.deleted_count != 1:
        return False

    return True

def queryElement(mongoConnection: MongoClient, collection: str, username: str) -> Dict | None:
    db = mongoConnection["ISIS2503-Sprint4"]
    col = db[collection]
    print(username)

    res = col.find_one({"username": username}, sort=[("version", pymongo.DESCENDING)])

    return res
