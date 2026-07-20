import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Forge"
    
    # Database Configuration
    # Fallback to postgresql+asyncpg for production, or sqlite+aiosqlite for local tests
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/forge"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Clerk Authentication Configurations
    CLERK_SECRET_KEY: str = "sk_test_placeholder_secret_key_value"
    CLERK_JWKS_URL: str = "https://api.clerk.com/v1/jwks"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    
    # Rate Limiting Configurations
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
