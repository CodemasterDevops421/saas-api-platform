from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SaaS API Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/saas_api"
    REDIS_URL: str = "redis://localhost:6379/0"
    STRIPE_SECRET_KEY: str = "sk_test_"
    STRIPE_WEBHOOK_SECRET: str = "whsec_"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    class Config:
        env_file = ".env"

settings = Settings()