from redis import Redis
from ..config import settings
from datetime import datetime, timedelta
from typing import Dict, List

class AnalyticsService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        
    def track_request(self, api_key: str, endpoint: str, response_time: float):
        """Track an API request"""
        now = datetime.utcnow()
        date_key = now.strftime("%Y-%m-%d")
        hour_key = now.strftime("%Y-%m-%d-%H")
        
        # Increment daily request count
        self.redis.incr(f"requests:{api_key}:{date_key}")
        
        # Track hourly request count
        self.redis.incr(f"requests:{api_key}:{hour_key}")
        
        # Track response time
        self.redis.lpush(
            f"response_times:{api_key}:{date_key}",
            response_time
        )
        self.redis.ltrim(
            f"response_times:{api_key}:{date_key}",
            0,
            999
        )  # Keep last 1000 responses
        
    def get_usage_stats(
        self,
        api_key: str,
        days: int = 30
    ) -> Dict[str, List]:
        """Get usage statistics for an API key"""
        stats = {
            "daily_requests": [],
            "response_times": [],
            "total_requests": 0
        }
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            
            # Get daily requests
            requests = int(self.redis.get(
                f"requests:{api_key}:{date_key}"
            ) or 0)
            
            # Get response times
            times = self.redis.lrange(
                f"response_times:{api_key}:{date_key}",
                0,
                -1
            )
            avg_time = sum(float(t) for t in times) / len(times) if times else 0
            
            stats["daily_requests"].append({
                "date": date_key,
                "count": requests
            })
            stats["response_times"].append({
                "date": date_key,
                "average_ms": avg_time
            })
            stats["total_requests"] += requests
            
            current_date += timedelta(days=1)
        
        return stats