from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class APIKeyCreate(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class APIKey(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True