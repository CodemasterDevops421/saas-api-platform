from fastapi import Request
from ..services.analytics_service import AnalyticsService
from time import time

analytics_service = AnalyticsService()

async def analytics_middleware(request: Request, call_next):
    start_time = time()
    
    response = await call_next(request)
    
    # Track API usage if this is an API request
    if request.url.path.startswith("/api/v1/"):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            response_time = (time() - start_time) * 1000  # Convert to milliseconds
            analytics_service.track_request(
                api_key=api_key,
                endpoint=request.url.path,
                response_time=response_time
            )
    
    return response