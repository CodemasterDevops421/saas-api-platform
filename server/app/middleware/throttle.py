from fastapi import Request, HTTPException
from redis import Redis
from typing import Optional
import time

class ThrottleMiddleware:
    def __init__(self, redis: Redis, window: int = 60, limit: Optional[int] = None):
        self.redis = redis
        self.window = window
        self.default_limit = limit
        
    async def __call__(self, request: Request, call_next):
        user_id = request.state.user.id if hasattr(request.state, 'user') else None
        client_ip = request.client.host
        
        limit = await self._get_rate_limit(user_id)
        key = f"throttle:{client_ip}:{user_id}"
        
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, self.window)
            
        if current > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
        return await call_next(request)
        
    async def _get_rate_limit(self, user_id: Optional[int]) -> int:
        if not user_id:
            return self.default_limit or 100
            
        key = f"user:{user_id}:tier"
        tier = self.redis.get(key)
        
        limits = {
            'basic': 1000,
            'pro': 5000,
            'enterprise': 20000
        }
        return limits.get(tier, self.default_limit or 100)