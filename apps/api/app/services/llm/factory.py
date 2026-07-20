"""LLM Provider Factory with Automatic Failover."""

from __future__ import annotations

from app.config.settings import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_mock import local_mock_llm_provider
from app.services.llm.providers import AnthropicLLMProvider, OllamaLLMProvider, OpenAILLMProvider


class LLMProviderFactory:
    """
    Factory creating LLM Provider instances with local fallback.
    """

    def get_provider(self, provider_name: str | None = None) -> BaseLLMProvider:
        p_name = (provider_name or settings.LLM_PROVIDER).lower()
        if p_name == "openai":
            return OpenAILLMProvider()
        elif p_name == "anthropic":
            return AnthropicLLMProvider()
        elif p_name == "ollama":
            return OllamaLLMProvider()
        return local_mock_llm_provider


llm_provider_factory = LLMProviderFactory()
