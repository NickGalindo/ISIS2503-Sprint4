from typing import Dict, Any
from datetime import timedelta
import redis
from colorama import Fore

from decimal import Decimal

import json
from datetime import datetime

class MultiEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                "__type": "datetime",
                "value": obj.isoformat()
            }
        if isinstance(obj, Decimal):
            return float(obj)
        return super(MultiEncoder, self).default(obj)

class MultiDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "__type" not in obj:
            return obj

        if obj["__type"] == "datetime":
            return datetime.fromisoformat(obj["value"])

        return obj

def checkJwtBlacklist(redis_connection_pool: redis.ConnectionPool, token: str):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    try:
        if __redis.get(token) is not None:
            return True
    except Exception as e:
        print(Fore.RED + "ERROR: Failed to check jwt blacklist falling back to default blacklisted")
        print(e)
        return True

    return False

def addJwtBlacklist(redis_connection_pool: redis.ConnectionPool, token: str, exp: timedelta):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    try:
        __redis.setex(token, exp, 1)
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't blacklist jwt token")
        print(e)
        return False

    return True

def getUser(redis_connection_pool: redis.ConnectionPool, username: str):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    try:
        val = __redis.get(username)
    except Exception as e:
        print(Fore.RED + f"ERROR: Failed to get user session from cache")
        print(e)
        return None

    if val is None:
        return None

    if not isinstance(val, str):
        print(Fore.RED + f"ERROR: Error validating user session")
        print(val)
        return None

    loaded_val = json.loads(val, cls=MultiDecoder)
    if not isinstance(loaded_val, Dict):
        print(Fore.RED + f"ERROR: Error validating user session")
        print(loaded_val)
        return None

    return loaded_val

def setUser(redis_connection_pool: redis.ConnectionPool, username: str, value: Any):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    __serialized_value = json.dumps(value, cls=MultiEncoder)
    try:
        __redis.set(username, __serialized_value)
    except Exception as e:
        print(Fore.RED + f"Error while saving into redis:\n{e}")
        return False

    return True
