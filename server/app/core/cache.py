from functools import wraps
from typing import Optional
import json
from redis import Redis
from ..core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cache(ttl_seconds: int = 300, prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not prefix:
                cache_prefix = f"{func.__module__}:{func.__name__}"
            else:
                cache_prefix = prefix

            cache_key = cache_key_builder(cache_prefix, *args, **kwargs)
            cached_data = redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            result = await func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator

def invalidate_cache(prefix: str, *args, **kwargs):
    pattern = cache_key_builder(prefix, *args, **kwargs)
    keys = redis_client.keys(f"{pattern}*")
    if keys:
        redis_client.delete(*keys)