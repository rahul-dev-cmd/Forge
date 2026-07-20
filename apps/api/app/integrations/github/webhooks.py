"""GitHub webhook signature verification and event parsing."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from app.config.settings import settings


SUPPORTED_EVENTS = frozenset(
    {
        "installation",
        "installation_repositories",
        "repository",
        "push",
        "pull_request",
        "issues",
        "create",
        "delete",
        "release",
        "ping",
    }
)


def verify_webhook_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """
    Verify X-Hub-Signature-256 using the configured webhook secret.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    secret = settings.GITHUB_APP_WEBHOOK_SECRET.encode("utf-8")
    expected = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)


def parse_webhook_payload(payload_body: bytes) -> dict[str, Any]:
    return json.loads(payload_body.decode("utf-8"))


def extract_installation_id(payload: dict[str, Any]) -> str | None:
    installation = payload.get("installation") or {}
    inst_id = installation.get("id")
    return str(inst_id) if inst_id is not None else None


def extract_repository_id(payload: dict[str, Any]) -> str | None:
    repo = payload.get("repository") or {}
    repo_id = repo.get("id")
    return str(repo_id) if repo_id is not None else None
