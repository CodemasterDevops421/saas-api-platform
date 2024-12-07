from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..db.session import get_db
from ..core.auth import get_current_user
from ..services.analytics_service import AnalyticsService
from ..core.pagination import PageParams, Page
from ..core.cache import cache

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/usage")
@cache(ttl_seconds=300)
async def get_usage_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    interval: str = Query("day", regex="^(hour|day|week|month)$"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    return await AnalyticsService.get_usage_stats(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )

@router.get("/requests", response_model=Page[dict])
@cache(ttl_seconds=60)
async def get_requests(
    params: PageParams = Depends(),
    status_code: Optional[int] = None,
    endpoint: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await AnalyticsService.get_requests(
        db=db,
        user_id=current_user.id,
        status_code=status_code,
        endpoint=endpoint,
        offset=params.offset,
        limit=params.size
    )