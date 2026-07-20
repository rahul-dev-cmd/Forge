"""Jina AI Embedding Provider implementation."""

from __future__ import annotations

import httpx
from app.config.settings import settings
from app.services.embedding.base import BaseEmbeddingProvider
from app.utils.logger import logger


class JinaEmbeddingProvider(BaseEmbeddingProvider):
    """
    Jina AI Embeddings API client (jina-embeddings-v2-base-code).
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.JINA_API_KEY
        self.model = model or "jina-embeddings-v2-base-code"
        self.dimensions = 768

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            logger.warning("Jina API key missing; falling back to local provider")
            from app.services.embedding.local_provider import local_embedding_provider
            return await local_embedding_provider.embed_texts(texts)

        url = "https://api.jina.ai/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": texts, "model": self.model}

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return [item["embedding"] for item in data["data"]]

    def get_dimensions(self) -> int:
        return self.dimensions

    def get_model_name(self) -> str:
        return self.model
