from redis import Redis, RedisCluster
from typing import Any, Optional, List
import json
import time
from prometheus_client import Counter, Histogram

class CacheManager:
    def __init__(self, redis_urls: List[str], max_connections: int = 50):
        self.cluster = RedisCluster.from_url(
            redis_urls[0],
            startup_nodes=[{'host': url} for url in redis_urls],
            max_connections=max_connections
        )
        
        self.hits = Counter('cache_hits_total', 'Cache hits')
        self.misses = Counter('cache_misses_total', 'Cache misses')
        self.latency = Histogram('cache_operation_seconds', 'Cache operation latency')

    async def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        try:
            value = self.cluster.get(key)
            if value:
                self.hits.inc()
                return json.loads(value)
            self.misses.inc()
            return None
        finally:
            self.latency.observe(time.time() - start_time)

    async def set(self, key: str, value: Any, expire: int = 3600):
        start_time = time.time()
        try:
            self.cluster.setex(
                key,
                expire,
                json.dumps(value)
            )
        finally:
            self.latency.observe(time.time() - start_time)

    async def invalidate_pattern(self, pattern: str):
        keys = self.cluster.keys(pattern)
        if keys:
            self.cluster.delete(*keys)

    def get_stats(self):
        stats = self.cluster.info()
        return {
            'hits': stats['keyspace_hits'],
            'misses': stats['keyspace_misses'],
            'memory_used': stats['used_memory'],
            'evicted_keys': stats['evicted_keys'],
            'connected_clients': stats['connected_clients']
        }