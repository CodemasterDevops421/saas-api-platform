from functools import wraps
from typing import Optional
from redis import Redis
from redis.connection import ConnectionPool
from ..core.config import settings

redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    decode_responses=True
)

redis_client = Redis(connection_pool=redis_pool)

class CacheManager:
    @staticmethod
    async def get_or_set(key: str, callback, expire: int = 300):
        cached = redis_client.get(key)
        if cached:
            return cached
            
        result = await callback()
        redis_client.setex(key, expire, result)
        return result
        
    @staticmethod
    async def invalidate_pattern(pattern: str):
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)