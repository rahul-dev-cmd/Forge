"""Categorized Production Secrets Architecture — Supports Env, Docker Secrets, and External Vaults."""

from __future__ import annotations

import abc
import os
from pathlib import Path
from typing import Any

from app.config.settings import settings


class BaseSecretManager(abc.ABC):
    """Abstract interface for Secrets Management."""

    @abc.abstractmethod
    def get_secret(self, key: str, default: str = "") -> str:
        pass


class EnvSecretManager(BaseSecretManager):
    """Environment Variable Secrets Provider."""

    def get_secret(self, key: str, default: str = "") -> str:
        return os.environ.get(key, getattr(settings, key, default))


class DockerSecretManager(BaseSecretManager):
    """Docker Secrets Provider reading from /run/secrets/."""

    def get_secret(self, key: str, default: str = "") -> str:
        secret_path = Path("/run/secrets") / key.lower()
        if secret_path.exists():
            return secret_path.read_text(encoding="utf-8").strip()
        return EnvSecretManager().get_secret(key, default)


class SecretsManager:
    """
    Unified Categorized Secrets Manager.
    Categories: llm, github, database, redis, qdrant, auth
    """

    def __init__(self, provider: BaseSecretManager | None = None):
        self.provider = provider or DockerSecretManager()

    def get_llm_key(self, provider_name: str) -> str:
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        env_key = key_map.get(provider_name.lower(), "OPENAI_API_KEY")
        return self.provider.get_secret(env_key)

    def get_github_app_private_key(self) -> str:
        return self.provider.get_secret("GITHUB_APP_PRIVATE_KEY")

    def get_database_url(self) -> str:
        return self.provider.get_secret("DATABASE_URL")

    def get_redis_url(self) -> str:
        return self.provider.get_secret("REDIS_URL")

    def get_qdrant_api_key(self) -> str:
        return self.provider.get_secret("QDRANT_API_KEY")

    def get_jwt_secret(self) -> str:
        return self.provider.get_secret("JWT_SECRET_KEY")


secrets_manager = SecretsManager()
