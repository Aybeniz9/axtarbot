import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()
r = redis.from_url(os.getenv("REDIS_URL"))

def get_cached(query: str):
    cached = r.get(f"search:{query}")
    return json.loads(cached) if cached else None

def set_cache(query: str, results, ttl=300):
    r.setex(f"search:{query}", ttl, json.dumps(results))