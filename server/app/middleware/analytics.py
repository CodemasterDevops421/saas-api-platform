from fastapi import Request
from sqlalchemy.orm import Session
from ..models.api_request import ApiRequest
from ..db.session import SessionLocal
import time

async def analytics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Skip analytics for internal endpoints
    if not request.url.path.startswith("/api/"):
        return response
    
    process_time = round((time.time() - start_time) * 1000)  # ms
    
    # Get user_id from request state if authenticated
    user_id = getattr(request.state, "user_id", None)
    
    if user_id:
        db = SessionLocal()
        try:
            db_request = ApiRequest(
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time=process_time
            )
            db.add(db_request)
            db.commit()
        finally:
            db.close()
    
    return response