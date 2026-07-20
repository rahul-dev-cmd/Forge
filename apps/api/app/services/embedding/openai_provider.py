"""OpenAI Embedding Provider implementation."""

from __future__ import annotations

import httpx
from app.config.settings import settings
from app.services.embedding.base import BaseEmbeddingProvider
from app.utils.logger import logger


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI Embeddings API client (text-embedding-3-small / text-embedding-3-large).
    """

    def __init__(self, api_key: str | None = None, model: str | None = None, dimensions: int = 1536):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or "text-embedding-3-small"
        self.dimensions = dimensions

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            logger.warning("OpenAI API key missing; falling back to local provider")
            from app.services.embedding.local_provider import local_embedding_provider
            return await local_embedding_provider.embed_texts(texts)

        url = "https://api.openai.com/v1/embeddings"
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
