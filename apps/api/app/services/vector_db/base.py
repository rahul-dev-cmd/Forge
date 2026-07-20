"""Vector Database Provider Base Abstract Class & Structures."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VectorPoint:
    id: str
    vector: list[float]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchResult:
    id: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)


class BaseVectorProvider(abc.ABC):
    """
    Abstract Vector Database Provider interface.
    Supports Qdrant, In-Memory, and extensible backends.
    """

    @abc.abstractmethod
    async def create_collection(self, collection_name: str, dimensions: int) -> bool:
        pass

    @abc.abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        pass

    @abc.abstractmethod
    async def upsert_vectors(self, collection_name: str, points: list[VectorPoint]) -> bool:
        pass

    @abc.abstractmethod
    async def delete_vectors(self, collection_name: str, vector_ids: list[str]) -> bool:
        pass

    @abc.abstractmethod
    async def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        pass
