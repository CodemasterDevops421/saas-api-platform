from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models.api_request import ApiRequest

async def get_user_usage_stats(db: Session, user_id: int):
    # Get last 30 days of usage
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Daily request count
    daily_requests = db.query(
        func.date(ApiRequest.created_at).label('date'),
        func.count(ApiRequest.id).label('count')
    ).filter(
        ApiRequest.user_id == user_id,
        ApiRequest.created_at >= thirty_days_ago
    ).group_by(
        func.date(ApiRequest.created_at)
    ).all()
    
    # Average response time
    avg_response_time = db.query(
        func.avg(ApiRequest.response_time)
    ).filter(
        ApiRequest.user_id == user_id,
        ApiRequest.created_at >= thirty_days_ago
    ).scalar()
    
    # Status code distribution
    status_codes = db.query(
        ApiRequest.status_code,
        func.count(ApiRequest.id).label('count')
    ).filter(
        ApiRequest.user_id == user_id,
        ApiRequest.created_at >= thirty_days_ago
    ).group_by(
        ApiRequest.status_code
    ).all()
    
    # Endpoint popularity
    popular_endpoints = db.query(
        ApiRequest.endpoint,
        func.count(ApiRequest.id).label('count')
    ).filter(
        ApiRequest.user_id == user_id,
        ApiRequest.created_at >= thirty_days_ago
    ).group_by(
        ApiRequest.endpoint
    ).order_by(
        func.count(ApiRequest.id).desc()
    ).limit(5).all()
    
    return {
        "daily_requests": [
            {"date": str(date), "count": count}
            for date, count in daily_requests
        ],
        "avg_response_time": round(avg_response_time, 2) if avg_response_time else 0,
        "status_codes": [
            {"code": code, "count": count}
            for code, count in status_codes
        ],
        "popular_endpoints": [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in popular_endpoints
        ]
    }