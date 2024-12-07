from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..db.base_class import Base

class ApiRequest(Base):
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    response_time = Column(Integer)  # in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())