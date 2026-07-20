"""Embedding Provider Base Interface."""

from __future__ import annotations

import abc


class BaseEmbeddingProvider(abc.ABC):
    """
    Abstract interface for Embedding Providers (OpenAI, Voyage AI, Jina AI, Local).
    """

    @abc.abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embedding vectors for a batch of text strings.
        """
        pass

    @abc.abstractmethod
    def get_dimensions(self) -> int:
        pass

    @abc.abstractmethod
    def get_model_name(self) -> str:
        pass
