from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ..monitoring.prometheus import (
    HTTP_REQUEST_COUNTER,
    HTTP_REQUEST_DURATION,
    ACTIVE_REQUESTS,
    API_KEY_USAGE
)
from ..monitoring.logger import logger
import time

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        ACTIVE_REQUESTS.inc()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            HTTP_REQUEST_COUNTER.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Record API key usage if present
            api_key = request.headers.get('X-API-Key')
            if api_key:
                API_KEY_USAGE.labels(api_key_id=api_key).inc()
            
            # Log request details
            logger.info(
                'Request completed',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'client_ip': request.client.host
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                'Request failed',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'error': str(e)
                },
                exc_info=True
            )
            raise
        
        finally:
            ACTIVE_REQUESTS.dec()