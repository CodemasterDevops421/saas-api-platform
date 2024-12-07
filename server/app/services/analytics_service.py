from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..core.cache import cache

class AnalyticsService:
    @staticmethod
    @cache(ttl_seconds=300, prefix="analytics:usage")
    async def get_usage_stats(db: Session, user_id: int, days: int = 30):
        start_date = datetime.utcnow() - timedelta(days=days)
        
        daily_stats = db.query(
            func.date(ApiRequest.created_at).label('date'),
            func.count(ApiRequest.id).label('count')
        ).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_date
        ).group_by(
            func.date(ApiRequest.created_at)
        ).all()

        endpoint_stats = db.query(
            ApiRequest.endpoint,
            func.count(ApiRequest.id).label('count')
        ).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_date
        ).group_by(
            ApiRequest.endpoint
        ).order_by(
            func.count(ApiRequest.id).desc()
        ).limit(10).all()

        return {
            "daily_stats": [
                {"date": str(date), "count": count}
                for date, count in daily_stats
            ],
            "endpoint_stats": [
                {"endpoint": endpoint, "count": count}
                for endpoint, count in endpoint_stats
            ]
        }