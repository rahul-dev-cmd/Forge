"""Vector Database Provider Factory."""

from __future__ import annotations

from app.config.settings import settings
from app.services.vector_db.base import BaseVectorProvider
from app.services.vector_db.in_memory import in_memory_vector_provider
from app.services.vector_db.qdrant import QdrantVectorProvider


class VectorDBFactory:
    """
    Factory creating VectorProvider instances.
    """

    def __init__(self):
        self._qdrant = QdrantVectorProvider()

    def get_provider(self, provider_name: str | None = None) -> BaseVectorProvider:
        p_type = (provider_name or settings.VECTOR_DB_PROVIDER).lower()
        if p_type == "memory":
            return in_memory_vector_provider
        return self._qdrant


vector_db_factory = VectorDBFactory()
