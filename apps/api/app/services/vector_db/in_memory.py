"""In-Memory Vector Database Provider for local development & testing."""

from __future__ import annotations

import math
from typing import Any

from app.services.vector_db.base import BaseVectorProvider, VectorPoint, VectorSearchResult


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1)) or 1.0
    mag2 = math.sqrt(sum(b * b for b in v2)) or 1.0
    return dot / (mag1 * mag2)


class InMemoryVectorProvider(BaseVectorProvider):
    """
    In-memory vector database with cosine similarity search & metadata filtering.
    """

    def __init__(self):
        # collection_name -> dict[point_id, VectorPoint]
        self._collections: dict[str, dict[str, VectorPoint]] = {}

    async def create_collection(self, collection_name: str, dimensions: int) -> bool:
        if collection_name not in self._collections:
            self._collections[collection_name] = {}
        return True

    async def delete_collection(self, collection_name: str) -> bool:
        self._collections.pop(collection_name, None)
        return True

    async def upsert_vectors(self, collection_name: str, points: list[VectorPoint]) -> bool:
        if collection_name not in self._collections:
            self._collections[collection_name] = {}
        for p in points:
            self._collections[collection_name][p.id] = p
        return True

    async def delete_vectors(self, collection_name: str, vector_ids: list[str]) -> bool:
        col = self._collections.get(collection_name, {})
        for vid in vector_ids:
            col.pop(vid, None)
        return True

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        col = self._collections.get(collection_name, {})
        if not col:
            return []

        scored: list[VectorSearchResult] = []
        for point in col.values():
            # Check metadata filters
            if filters:
                match = True
                for k, v in filters.items():
                    if str(point.payload.get(k)) != str(v):
                        match = False
                        break
                if not match:
                    continue

            score = cosine_similarity(query_vector, point.vector)
            scored.append(VectorSearchResult(id=point.id, score=score, payload=point.payload))

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:limit]


in_memory_vector_provider = InMemoryVectorProvider()
