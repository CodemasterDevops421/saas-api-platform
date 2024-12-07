from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum

class PlanTier(enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    tier = Column(Enum(PlanTier))
    price_monthly = Column(Float)
    price_yearly = Column(Float)
    request_limit = Column(Integer)
    features = Column(String)
    stripe_price_id = Column(String)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    stripe_subscription_id = Column(String)
    stripe_customer_id = Column(String)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    status = Column(String)
    
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan")