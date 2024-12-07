from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..core.config import settings
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..models.api_key import ApiKey
import redis
import json

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def rate_limit_middleware(request: Request, call_next):
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return await call_next(request)

    # Get rate limit for API key
    db = next(get_db())
    key_record = db.query(ApiKey).filter(ApiKey.key == api_key).first()
    if not key_record:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API key"}
        )

    # Check rate limit
    key = f"rate_limit:{api_key}"
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(
            key,
            60,  # 1 minute window
            json.dumps({"count": 1, "first_request": datetime.utcnow().isoformat()})
        )
    else:
        data = json.loads(current)
        if data["count"] >= settings.API_RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "reset_at": (datetime.fromisoformat(data["first_request"]) + 
                                timedelta(minutes=1)).isoformat()
                }
            )
        data["count"] += 1
        redis_client.setex(key, 60, json.dumps(data))

    response = await call_next(request)
    return response