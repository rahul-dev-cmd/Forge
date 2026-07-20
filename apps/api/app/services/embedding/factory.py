"""Embedding Provider Factory."""

from __future__ import annotations

from app.config.settings import settings
from app.services.embedding.base import BaseEmbeddingProvider
from app.services.embedding.jina_provider import JinaEmbeddingProvider
from app.services.embedding.local_provider import local_embedding_provider
from app.services.embedding.openai_provider import OpenAIEmbeddingProvider
from app.services.embedding.voyage_provider import VoyageEmbeddingProvider


class EmbeddingProviderFactory:
    """
    Factory creating embedding provider instances based on configuration.
    """

    def get_provider(self, provider_name: str | None = None) -> BaseEmbeddingProvider:
        p_type = (provider_name or settings.EMBEDDING_PROVIDER).lower()
        if p_type == "openai":
            return OpenAIEmbeddingProvider()
        elif p_type == "voyage":
            return VoyageEmbeddingProvider()
        elif p_type == "jina":
            return JinaEmbeddingProvider()
        return local_embedding_provider


embedding_provider_factory = EmbeddingProviderFactory()
