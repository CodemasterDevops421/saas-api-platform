from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request

HTTP_REQUEST_COUNTER = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

API_KEY_USAGE = Counter(
    'api_key_requests_total',
    'Total requests per API key',
    ['api_key_id']
)

SUBSCRIPTION_GAUGE = Gauge(
    'active_subscriptions',
    'Number of active subscriptions',
    ['plan']
)