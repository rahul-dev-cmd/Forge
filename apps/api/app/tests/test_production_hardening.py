"""Tests for Milestone 10 — Production Hardening, Collaboration & Launch."""

import pytest
from app.core.secrets_manager import secrets_manager
from app.services.cache import cache_service
from app.core.telemetry import telemetry_metrics
from app.services.feature_flags import feature_flag_service


@pytest.mark.asyncio
async def test_secrets_manager_categories():
    key = secrets_manager.get_llm_key("openai")
    assert isinstance(key, str)

    db_url = secrets_manager.get_database_url()
    assert isinstance(db_url, str)


@pytest.mark.asyncio
async def test_cache_service():
    await cache_service.set("test_key", {"foo": "bar"}, ttl_seconds=10)
    cached = await cache_service.get("test_key")
    assert cached == {"foo": "bar"}

    await cache_service.delete("test_key")
    deleted = await cache_service.get("test_key")
    assert deleted is None


def test_telemetry_metrics_exporter():
    telemetry_metrics.record_request(200)
    telemetry_metrics.record_tokens(100, 50)
    telemetry_metrics.record_cache(True)

    text_output = telemetry_metrics.generate_prometheus_text()
    assert "forge_http_requests_total" in text_output
    assert "forge_llm_prompt_tokens_total" in text_output
    assert "forge_cache_hits_total" in text_output


@pytest.mark.asyncio
async def test_feature_flag_service():
    enabled = await feature_flag_service.is_enabled("experimental_ai")
    assert enabled is True
