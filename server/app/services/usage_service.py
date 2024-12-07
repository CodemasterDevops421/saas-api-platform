from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List
from ..models.api_request import ApiRequest
from ..models.subscription import Subscription, SubscriptionTier
from ..core.exceptions import ValidationError

class UsageService:
    @staticmethod
    def track_request(
        db: Session,
        user_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float
    ) -> ApiRequest:
        request = ApiRequest(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time
        )
        db.add(request)
        db.commit()
        return request

    @staticmethod
    def check_usage_limits(db: Session, user_id: int) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()

        if not subscription:
            return False

        # Get subscription tier limits
        tier_limits = {
            SubscriptionTier.FREE: 1000,
            SubscriptionTier.BASIC: 10000,
            SubscriptionTier.PRO: 100000,
            SubscriptionTier.ENTERPRISE: float('inf')
        }

        # Count this month's requests
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        monthly_requests = db.query(func.count(ApiRequest.id)).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_of_month
        ).scalar()

        return monthly_requests < tier_limits.get(subscription.tier, tier_limits[SubscriptionTier.FREE])

    @staticmethod
    def get_usage_stats(db: Session, user_id: int, days: int = 30) -> Dict:
        start_date = datetime.utcnow() - timedelta(days=days)

        # Daily requests
        daily_requests = db.query(
            func.date(ApiRequest.created_at).label('date'),
            func.count(ApiRequest.id).label('count')
        ).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_date
        ).group_by(
            func.date(ApiRequest.created_at)
        ).all()

        # Endpoint popularity
        popular_endpoints = db.query(
            ApiRequest.endpoint,
            func.count(ApiRequest.id).label('count')
        ).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_date
        ).group_by(
            ApiRequest.endpoint
        ).order_by(
            func.count(ApiRequest.id).desc()
        ).limit(5).all()

        # Response time stats
        response_times = db.query(
            func.avg(ApiRequest.response_time).label('avg'),
            func.min(ApiRequest.response_time).label('min'),
            func.max(ApiRequest.response_time).label('max')
        ).filter(
            ApiRequest.user_id == user_id,
            ApiRequest.created_at >= start_date
        ).first()

        return {
            "daily_requests": [
                {"date": str(date), "count": count}
                for date, count in daily_requests
            ],
            "popular_endpoints": [
                {"endpoint": endpoint, "count": count}
                for endpoint, count in popular_endpoints
            ],
            "response_times": {
                "average": round(response_times.avg, 2) if response_times.avg else 0,
                "min": round(response_times.min, 2) if response_times.min else 0,
                "max": round(response_times.max, 2) if response_times.max else 0
            }
        }