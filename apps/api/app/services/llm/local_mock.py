"""Local Mock LLM Provider for deterministic offline testing & local development."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator, Any

from app.services.llm.base import BaseLLMProvider


class LocalMockLLMProvider(BaseLLMProvider):
    """
    Deterministic Local LLM Provider with streaming support.
    """

    async def generate_text(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2
    ) -> str:
        return (
            f"Analysis complete for query: '{prompt[:60]}...'. "
            "Based on the repository context, the system architecture follows clean modular principles with defined boundaries."
        )

    async def stream_text(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        response = (
            f"Analysis complete for query: '{prompt[:60]}...'. "
            "Based on the repository context, the codebase exhibits strong architectural patterns, "
            "well-defined module boundaries, and proper abstraction layers."
        )
        words = response.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.01)

    async def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        return {
            "intent": "EXPLAIN",
            "agent": "CodeExplainer",
            "answer": f"Parsed query and retrieved relevant context for: {prompt[:50]}",
            "confidence": 0.94,
            "citations": [],
            "followups": ["Would you like to inspect dependent modules?", "Show call graph?"],
        }

    def get_provider_name(self) -> str:
        return "local"

    def get_model_name(self) -> str:
        return "local-mock-v1"


local_mock_llm_provider = LocalMockLLMProvider()
