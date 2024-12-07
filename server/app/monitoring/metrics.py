from prometheus_client import Counter, Histogram, Gauge
from typing import Callable
from functools import wraps
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Cache metrics
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses')
CACHE_SIZE = Gauge('cache_size_bytes', 'Total cache size in bytes')

# Database metrics
DB_CONNECTIONS = Gauge('db_connections_total', 'Total active DB connections')
QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

def track_request_metrics(handler: Callable):
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        method = args[1].method
        path = args[1].url.path
        start_time = time.time()
        
        try:
            response = await handler(*args, **kwargs)
            status = response.status_code
            return response
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
    
    return wrapper