"""Local Lightweight Feature-Hashing Embedding Provider."""

from __future__ import annotations

import hashlib
import math
from app.services.embedding.base import BaseEmbeddingProvider


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic 384-dimensional feature-hashing embedding provider.
    Zero external dependencies; ideal for offline testing & local development.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dimensions
            words = text.lower().split()
            for word in words:
                # Hash word to dimension index
                h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimensions
                sign = 1.0 if (h % 2) == 0 else -1.0
                vec[idx] += sign

            # Normalize vector
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            normalized = [round(x / norm, 6) for x in vec]
            embeddings.append(normalized)

        return embeddings

    def get_dimensions(self) -> int:
        return self.dimensions

    def get_model_name(self) -> str:
        return "all-MiniLM-L6-v2-local"


local_embedding_provider = LocalEmbeddingProvider()
