from sqlalchemy import text
from typing import List

def create_performance_indexes(session) -> List[str]:
    indexes = [
        # API requests indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_user_date ON api_requests(user_id, created_at DESC)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_endpoint ON api_requests(endpoint, created_at DESC)",
        
        # User indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_status ON users(status) WHERE status != 'inactive'",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription ON users(subscription_status, subscription_end_date)",
        
        # Subscription indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, status) WHERE status = 'active'",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscriptions_expire ON subscriptions(current_period_end) WHERE status = 'active'"
    ]
    
    created = []
    for index in indexes:
        try:
            session.execute(text(index))
            session.commit()
            created.append(index)
        except Exception as e:
            session.rollback()
            print(f"Error creating index: {str(e)}")
    
    return created