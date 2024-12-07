from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SubscriptionBase(BaseModel):
    price_id: str

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: str
    status: str
    current_period_end: datetime

    class Config:
        from_attributes = True