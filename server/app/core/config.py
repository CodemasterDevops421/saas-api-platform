from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # Redis settings
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_POOL_SIZE: int = 20
    
    # Rate limiting
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # Cache settings
    CACHE_TTL: int = 300
    
    # Performance tuning
    WORKER_PROCESSES: int = 4
    WORKER_CONNECTIONS: int = 1000
    KEEPALIVE_TIMEOUT: int = 65
    
    class Config:
        env_file = ".env"