from fastapi import Request, HTTPException
from redis import Redis
from ..config import settings
from ..crud import get_api_key_by_token
from datetime import datetime

redis = Redis.from_url(settings.REDIS_URL)

async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1/"):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Get rate limit for the API key's plan
            key = f"rate_limit:{api_key}"
            minute_key = f"{key}:minute"
            day_key = f"{key}:day"
            
            # Check minute limit
            minute_requests = redis.get(minute_key)
            if minute_requests and int(minute_requests) > 100:  # 100 requests per minute
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please upgrade your plan for higher limits."
                )
            
            # Check daily limit
            day_requests = redis.get(day_key)
            if day_requests and int(day_requests) > 10000:  # 10000 requests per day
                raise HTTPException(
                    status_code=429,
                    detail="Daily rate limit exceeded. Please try again tomorrow or upgrade your plan."
                )
            
            # Increment counters
            pipe = redis.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)  # Reset after 1 minute
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)  # Reset after 24 hours
            pipe.execute()
    
    response = await call_next(request)
    return response