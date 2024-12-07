from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .... import models
from ....database import get_db
from ....services.analytics_service import AnalyticsService
from typing import Optional

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/usage")
async def get_usage_stats(
    api_key_id: int,
    days: Optional[int] = 30,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_key = crud.get_api_key(db, api_key_id)
    if not api_key or api_key.user_id != user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    
    stats = analytics_service.get_usage_stats(api_key.key, days)
    return stats