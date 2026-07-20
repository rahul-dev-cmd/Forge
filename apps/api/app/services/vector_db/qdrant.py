"""Qdrant Vector Provider implementation."""

from __future__ import annotations

import httpx
from typing import Any

from app.config.settings import settings
from app.services.vector_db.base import BaseVectorProvider, VectorPoint, VectorSearchResult
from app.utils.logger import logger


class QdrantVectorProvider(BaseVectorProvider):
    """
    Qdrant Vector Database implementation supporting qdrant-client SDK or HTTP REST fallback.
    """

    def __init__(self, host: str | None = None, port: int | None = None, api_key: str | None = None):
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.api_key = api_key or settings.QDRANT_API_KEY
        self.base_url = f"http://{self.host}:{self.port}"

    async def create_collection(self, collection_name: str, dimensions: int) -> bool:
        url = f"{self.base_url}/collections/{collection_name}"
        payload = {"vectors": {"size": dimensions, "distance": "Cosine"}}
        headers = {"api-key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.put(url, json=payload, headers=headers)
                return res.status_code in (200, 201)
            except Exception as e:
                logger.warning("Qdrant connection error during collection creation", extra={"error": str(e)})
                return False

    async def delete_collection(self, collection_name: str) -> bool:
        url = f"{self.base_url}/collections/{collection_name}"
        headers = {"api-key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.delete(url, headers=headers)
                return res.status_code == 200
            except Exception as e:
                logger.warning("Qdrant delete collection error", extra={"error": str(e)})
                return False

    async def upsert_vectors(self, collection_name: str, points: list[VectorPoint]) -> bool:
        url = f"{self.base_url}/collections/{collection_name}/points?wait=true"
        headers = {"api-key": self.api_key} if self.api_key else {}
        body = {
            "points": [
                {"id": p.id, "vector": p.vector, "payload": p.payload}
                for p in points
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.put(url, json=body, headers=headers)
                return res.status_code == 200
            except Exception as e:
                logger.error("Qdrant upsert failed", extra={"error": str(e)})
                return False

    async def delete_vectors(self, collection_name: str, vector_ids: list[str]) -> bool:
        url = f"{self.base_url}/collections/{collection_name}/points/delete?wait=true"
        headers = {"api-key": self.api_key} if self.api_key else {}
        body = {"points": vector_ids}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.post(url, json=body, headers=headers)
                return res.status_code == 200
            except Exception as e:
                logger.error("Qdrant vector deletion error", extra={"error": str(e)})
                return False

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        url = f"{self.base_url}/collections/{collection_name}/points/search"
        headers = {"api-key": self.api_key} if self.api_key else {}
        
        qdrant_filter = None
        if filters:
            must_clauses = []
            for k, v in filters.items():
                must_clauses.append({"key": k, "match": {"value": str(v)}})
            qdrant_filter = {"must": must_clauses}

        body: dict[str, Any] = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True,
        }
        if qdrant_filter:
            body["filter"] = qdrant_filter

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.post(url, json=body, headers=headers)
                if res.status_code != 200:
                    return []
                data = res.json()
                results = []
                for item in data.get("result", []):
                    results.append(
                        VectorSearchResult(
                            id=str(item["id"]),
                            score=float(item.get("score", 0.0)),
                            payload=item.get("payload", {}),
                        )
                    )
                return results
            except Exception as e:
                logger.error("Qdrant search error", extra={"error": str(e)})
                return []
