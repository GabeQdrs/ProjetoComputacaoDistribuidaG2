import redis
import json

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

def get_cache(key):
    value = r.get(key)

    if value:
        return json.loads(value)

    return None

def set_cache(key, data):
    r.set(key, json.dumps(data), ex=60)

def delete_cache(key):
    r.delete(key)