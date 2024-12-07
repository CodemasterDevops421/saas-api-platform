from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PlanTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class PlanBase(BaseModel):
    name: str
    tier: PlanTier
    price_monthly: float
    price_yearly: float
    request_limit: int
    features: List[str]

class PlanCreate(PlanBase):
    stripe_price_id: str

class Plan(PlanBase):
    id: int
    stripe_price_id: str

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    plan_id: int

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: str
    stripe_customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime

    class Config:
        from_attributes = True