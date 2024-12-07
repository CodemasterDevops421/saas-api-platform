from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from ..services.api_key_service import ApiKeyService
from ..db.session import get_db

async def verify_api_key(request: Request):
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )

    db = next(get_db())
    key = ApiKeyService.validate_api_key(db, api_key)
    
    if not key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key"
        )

    # Store validated key in request state
    request.state.api_key = key
    request.state.user_id = key.user_id