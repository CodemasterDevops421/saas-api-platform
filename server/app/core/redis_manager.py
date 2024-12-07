from redis.cluster import RedisCluster
from typing import Optional, Any
import json

class RedisManager:
    def __init__(self, hosts, password=None):
        self.client = RedisCluster(
            startup_nodes=hosts,
            password=password,
            decode_responses=True,
            skip_full_coverage_check=True
        )
    
    async def get_cached(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    async def set_cached(self, key: str, value: Any, expire: int = 3600):
        try:
            self.client.setex(
                name=key,
                time=expire,
                value=json.dumps(value)
            )
        except Exception:
            pass

    async def invalidate_keys(self, pattern: str):
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass