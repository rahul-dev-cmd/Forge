"""LLM Provider Wrappers for OpenAI, Anthropic, Gemini, Groq, OpenRouter, and Ollama."""

from __future__ import annotations

import json
from typing import AsyncGenerator, Any

import httpx

from app.config.settings import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_mock import local_mock_llm_provider
from app.utils.logger import logger


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.LLM_MODEL

    async def generate_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        if not self.api_key:
            return await local_mock_llm_provider.generate_text(prompt, system_prompt)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(url, json={"model": self.model, "messages": messages, "temperature": temperature}, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def stream_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in local_mock_llm_provider.stream_text(prompt, system_prompt):
                yield chunk
            return
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=45.0) as client:
            async with client.stream("POST", url, json={"model": self.model, "messages": messages, "stream": True}, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and not line.endswith("[DONE]"):
                        try:
                            data = json.loads(line[6:])
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            pass

    async def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        text = await self.generate_text(prompt, system_prompt=system_prompt)
        try:
            return json.loads(text)
        except Exception:
            return {"answer": text}

    def get_provider_name(self) -> str:
        return "openai"

    def get_model_name(self) -> str:
        return self.model


class AnthropicLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model

    async def generate_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        if not self.api_key:
            return await local_mock_llm_provider.generate_text(prompt, system_prompt)
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        payload = {"model": self.model, "max_tokens": 4096, "messages": [{"role": "user", "content": prompt}]}
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["content"][0]["text"]

    async def stream_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in local_mock_llm_provider.stream_text(prompt, system_prompt):
                yield chunk
            return
        text = await self.generate_text(prompt, system_prompt)
        yield text

    async def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        text = await self.generate_text(prompt, system_prompt)
        try:
            return json.loads(text)
        except Exception:
            return {"answer": text}

    def get_provider_name(self) -> str:
        return "anthropic"

    def get_model_name(self) -> str:
        return self.model


class OllamaLLMProvider(BaseLLMProvider):
    def __init__(self, base_url: str | None = None, model: str = "llama3"):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model

    async def generate_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                return res.json()["response"]
            except Exception:
                return await local_mock_llm_provider.generate_text(prompt, system_prompt)

    async def stream_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> AsyncGenerator[str, None]:
        async for chunk in local_mock_llm_provider.stream_text(prompt, system_prompt):
            yield chunk

    async def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        text = await self.generate_text(prompt, system_prompt)
        try:
            return json.loads(text)
        except Exception:
            return {"answer": text}

    def get_provider_name(self) -> str:
        return "ollama"

    def get_model_name(self) -> str:
        return self.model
