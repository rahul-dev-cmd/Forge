"""GitHub App authentication helpers — JWT + installation tokens. No PATs."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import jwt

from app.config.settings import settings
from app.utils.logger import logger


class GitHubAppAuthError(Exception):
    """Raised when GitHub App credentials are missing or token exchange fails."""


def _load_private_key() -> str:
    raw = settings.GITHUB_APP_PRIVATE_KEY.strip()
    if not raw:
        raise GitHubAppAuthError("GITHUB_APP_PRIVATE_KEY is not configured")
    if raw.startswith("-----BEGIN"):
        return raw.replace("\\n", "\n")
    path = Path(raw)
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Treat as PEM with escaped newlines
    return raw.replace("\\n", "\n")


def is_github_app_configured() -> bool:
    return bool(settings.GITHUB_APP_ID and settings.GITHUB_APP_PRIVATE_KEY)


def create_app_jwt(expires_in: int = 540) -> str:
    """
    Create a short-lived GitHub App JWT (max 10 minutes).
    """
    if not settings.GITHUB_APP_ID:
        raise GitHubAppAuthError("GITHUB_APP_ID is not configured")
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + expires_in,
        "iss": settings.GITHUB_APP_ID,
    }
    return jwt.encode(payload, _load_private_key(), algorithm="RS256")


async def get_installation_token(installation_id: str) -> tuple[str, datetime]:
    """
    Exchange App JWT for a short-lived installation access token.
    Returns (token, expires_at). Never log or return this token to clients.
    """
    app_jwt = create_app_jwt()
    url = f"{settings.GITHUB_API_BASE_URL}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers)
        if response.status_code == 404:
            raise GitHubAppAuthError(
                f"Installation {installation_id} not found or was deleted"
            )
        if response.status_code == 401:
            raise GitHubAppAuthError("GitHub App JWT rejected — check App ID and private key")
        if response.status_code == 403:
            raise GitHubAppAuthError(
                f"Permission revoked or suspended for installation {installation_id}"
            )
        response.raise_for_status()
        data = response.json()

    token = data["token"]
    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
    logger.info(
        "Issued GitHub installation token",
        extra={"installation_id": installation_id, "expires_at": expires_at.isoformat()},
    )
    return token, expires_at


async def exchange_oauth_code(code: str) -> dict:
    """
    Exchange OAuth user-to-server code for access/refresh tokens (account linking).
    """
    if not settings.GITHUB_APP_CLIENT_ID or not settings.GITHUB_APP_CLIENT_SECRET:
        raise GitHubAppAuthError("GitHub App OAuth client credentials are not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_APP_CLIENT_ID,
                "client_secret": settings.GITHUB_APP_CLIENT_SECRET,
                "code": code,
            },
        )
        response.raise_for_status()
        data = response.json()

    if "error" in data:
        raise GitHubAppAuthError(data.get("error_description") or data["error"])
    return data


def build_install_url(state: str | None = None) -> str:
    base = f"{settings.GITHUB_APP_URL.rstrip('/')}/{settings.GITHUB_APP_SLUG}/installations/new"
    if state:
        return f"{base}?state={state}"
    return base


def build_oauth_authorize_url(state: str) -> str:
    client_id = settings.GITHUB_APP_CLIENT_ID
    redirect = f"{settings.API_PUBLIC_URL}{settings.API_V1_STR}/github/callback"
    return (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}&redirect_uri={redirect}&state={state}"
    )
