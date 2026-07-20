"""Webhook signature verification and GitHub connect smoke tests."""

import hashlib
import hmac

import pytest
from httpx import AsyncClient

from app.config.settings import settings
from app.integrations.github.webhooks import verify_webhook_signature, SUPPORTED_EVENTS


def test_supported_webhook_events_cover_milestone():
    required = {
        "installation",
        "installation_repositories",
        "repository",
        "push",
        "pull_request",
        "issues",
        "create",
        "delete",
        "release",
    }
    assert required.issubset(SUPPORTED_EVENTS)


def test_verify_webhook_signature_valid():
    body = b'{"action":"created","installation":{"id":1}}'
    secret = settings.GITHUB_APP_WEBHOOK_SECRET.encode("utf-8")
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(body, f"sha256={digest}") is True


def test_verify_webhook_signature_invalid():
    body = b'{"action":"created"}'
    assert verify_webhook_signature(body, "sha256=deadbeef") is False
    assert verify_webhook_signature(body, None) is False


@pytest.mark.asyncio
async def test_github_connect_returns_urls(client: AsyncClient):
    response = await client.post(
        "/api/v1/github/connect",
        json={},
        headers={"Authorization": "Bearer mock-token-rahuldev"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "install_url" in payload["data"]
    assert "state" in payload["data"]


@pytest.mark.asyncio
async def test_webhook_rejects_bad_signature(client: AsyncClient):
    response = await client.post(
        "/api/v1/webhooks/github",
        content=b'{"zen":"test"}',
        headers={
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "delivery-test-1",
            "X-Hub-Signature-256": "sha256=invalid",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_accepts_valid_signature(client: AsyncClient):
    body = b'{"zen":"test","hook_id":1}'
    secret = settings.GITHUB_APP_WEBHOOK_SECRET.encode("utf-8")
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    response = await client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "delivery-test-2",
            "X-Hub-Signature-256": f"sha256={digest}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["accepted"] is True


@pytest.mark.asyncio
async def test_list_repositories_requires_filter(client: AsyncClient):
    response = await client.get(
        "/api/v1/repositories",
        headers={"Authorization": "Bearer mock-token-rahuldev"},
    )
    assert response.status_code == 400
