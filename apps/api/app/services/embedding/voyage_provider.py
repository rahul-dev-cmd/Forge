"""Voyage AI Embedding Provider implementation."""

from __future__ import annotations

import httpx
from app.config.settings import settings
from app.services.embedding.base import BaseEmbeddingProvider
from app.utils.logger import logger


class VoyageEmbeddingProvider(BaseEmbeddingProvider):
    """
    Voyage AI Embeddings API client (voyage-code-2).
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.VOYAGE_API_KEY
        self.model = model or "voyage-code-2"
        self.dimensions = 1536

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            logger.warning("Voyage API key missing; falling back to local provider")
            from app.services.embedding.local_provider import local_embedding_provider
            return await local_embedding_provider.embed_texts(texts)

        url = "https://api.voyageai.com/v1/embeddings"
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
