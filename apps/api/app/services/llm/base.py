"""LLM Provider Base Abstract Interface."""

from __future__ import annotations

import abc
from typing import AsyncGenerator, Any


class BaseLLMProvider(abc.ABC):
    """
    Abstract interface for LLM Providers (OpenAI, Anthropic, Gemini, Groq, OpenRouter, Ollama, Local).
    Supports text generation, async SSE event streaming, and structured JSON output.
    """

    @abc.abstractmethod
    async def generate_text(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2
    ) -> str:
        """Generate a complete text completion."""
        pass

    @abc.abstractmethod
    async def stream_text(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks asynchronously."""
        yield ""

    @abc.abstractmethod
    async def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Generate a structured JSON output."""
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_model_name(self) -> str:
        pass
