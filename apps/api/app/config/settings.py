import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Forge"

    # Database Configuration
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
        "http://localhost:8000",
    ]

    # Rate Limiting Configurations
    RATE_LIMIT_PER_MINUTE: int = 100

    # Credential encryption (Fernet key derived from this secret)
    CREDENTIALS_ENCRYPTION_KEY: str = "forge-dev-encryption-key-change-me"

    # GitHub App configuration (prefer App over PATs)
    GITHUB_APP_ID: str = ""
    GITHUB_APP_CLIENT_ID: str = ""
    GITHUB_APP_CLIENT_SECRET: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""  # PEM contents or path; newlines as \n
    GITHUB_APP_WEBHOOK_SECRET: str = "forge-dev-webhook-secret"
    GITHUB_APP_SLUG: str = "forge"
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_APP_URL: str = "https://github.com/apps"

    # Frontend callback base for OAuth redirects
    FRONTEND_URL: str = "http://localhost:3000"
    API_PUBLIC_URL: str = "http://localhost:8000"

    # Worker / sync tunables
    GITHUB_SYNC_COMMIT_LIMIT: int = 50
    GITHUB_SYNC_PR_LIMIT: int = 30
    GITHUB_SYNC_ISSUE_LIMIT: int = 30
    GITHUB_SYNC_BRANCH_LIMIT: int = 50
    SYNC_MAX_RETRIES: int = 3
    PERIODIC_SYNC_INTERVAL_SECONDS: int = 3600

    # Vector DB & Embedding Settings (Milestone 8)
    VECTOR_DB_PROVIDER: str = "qdrant"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "forge_vectors"

    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    EMBEDDING_BATCH_SIZE: int = 64

    OPENAI_API_KEY: str = ""
    VOYAGE_API_KEY: str = ""
    JINA_API_KEY: str = ""

    # LLM & Copilot Multi-Agent Settings (Milestone 9)
    LLM_PROVIDER: str = "local"
    LLM_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"



settings = Settings()

