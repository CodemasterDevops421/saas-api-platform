from fastapi import Request
from ..core.cache import redis_client
from ..core.config import settings
from ..models.subscription import SubscriptionTier

async def get_rate_limit(subscription_tier: SubscriptionTier) -> int:
    limits = {
        SubscriptionTier.FREE: 100,
        SubscriptionTier.BASIC: 1000,
        SubscriptionTier.PRO: 10000,
        SubscriptionTier.ENTERPRISE: 100000
    }
    return limits.get(subscription_tier, 100)

async def check_rate_limit(request: Request) -> bool:
    client_id = request.client.host
    key = f"rate_limit:{client_id}"
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, settings.RATE_LIMIT_WINDOW)
    current = pipe.execute()[0]
    
    # Get user's subscription tier
    user = request.state.user
    limit = await get_rate_limit(user.subscription_tier)
    
    return current <= limit