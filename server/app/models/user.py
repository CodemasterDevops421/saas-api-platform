from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base
import enum

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    subscription_status = Column(String)
    subscription_end_date = Column(DateTime)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    api_keys = relationship("ApiKey", back_populates="user")
    subscription = relationship("Subscription", back_populates="user")
    usage_logs = relationship("ApiRequest", back_populates="user")