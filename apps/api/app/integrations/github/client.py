"""Async GitHub REST API client using installation tokens. Metadata only — no clones."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.settings import settings
from app.integrations.github.app_auth import get_installation_token, GitHubAppAuthError
from app.utils.logger import logger


class GitHubAPIError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str = "github_api_error",
        rate_limit_remaining: int | None = None,
        rate_limit_reset: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.rate_limit_remaining = rate_limit_remaining
        self.rate_limit_reset = rate_limit_reset


class GitHubClient:
    def __init__(self, installation_id: str):
        self.installation_id = installation_id
        self._token: str | None = None
        self._token_expires: datetime | None = None
        # Latest observed rate-limit snapshot from response headers
        self.last_rate_limit: dict[str, int | None] | None = None

    async def _ensure_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and self._token_expires and self._token_expires > now:
            return self._token
        self._token, self._token_expires = await get_installation_token(self.installation_id)
        return self._token

    def _parse_rate_limit(
        self, response: httpx.Response
    ) -> tuple[int | None, int | None, int | None]:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        limit = response.headers.get("X-RateLimit-Limit")
        return (
            int(remaining) if remaining is not None else None,
            int(reset) if reset is not None else None,
            int(limit) if limit is not None else None,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        token = await self._ensure_token()
        url = path if path.startswith("http") else f"{settings.GITHUB_API_BASE_URL}{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.request(
                method, url, headers=headers, params=params, json=json_body
            )

        remaining, reset, limit = self._parse_rate_limit(response)
        self.last_rate_limit = {
            "remaining": remaining,
            "reset": reset,
            "limit": limit,
        }
        if remaining is not None and remaining < 50:
            logger.warning(
                "GitHub rate limit low",
                extra={
                    "installation_id": self.installation_id,
                    "remaining": remaining,
                    "limit": limit,
                    "reset": reset,
                },
            )

        if response.status_code == 401:
            # Token may have expired mid-flight — clear and signal retry
            self._token = None
            raise GitHubAPIError(
                "Installation token expired or invalid",
                status_code=401,
                error_code="installation_token_expired",
                rate_limit_remaining=remaining,
                rate_limit_reset=reset,
            )
        if response.status_code == 403:
            if remaining == 0:
                raise GitHubAPIError(
                    "GitHub API rate limit exceeded",
                    status_code=403,
                    error_code="rate_limit_exceeded",
                    rate_limit_remaining=remaining,
                    rate_limit_reset=reset,
                )
            raise GitHubAPIError(
                "GitHub permission denied — installation may be revoked or suspended",
                status_code=403,
                error_code="permission_revoked",
                rate_limit_remaining=remaining,
                rate_limit_reset=reset,
            )
        if response.status_code == 404:
            raise GitHubAPIError(
                "GitHub resource not found — repository may have been deleted or transferred",
                status_code=404,
                error_code="resource_not_found",
            )
        if response.status_code >= 400:
            raise GitHubAPIError(
                f"GitHub API error: {response.status_code} {response.text[:300]}",
                status_code=response.status_code,
            )

        if response.status_code == 204:
            return None
        return response.json()

    async def get_installation(self) -> dict:
        from app.integrations.github.app_auth import create_app_jwt

        app_jwt = create_app_jwt()
        url = f"{settings.GITHUB_API_BASE_URL}/app/installations/{self.installation_id}"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise GitHubAPIError(
                    f"Failed to fetch installation: {response.status_code}",
                    status_code=response.status_code,
                )
            return response.json()

    async def list_installation_repositories(self, page: int = 1, per_page: int = 50) -> dict:
        return await self.request(
            "GET",
            "/installation/repositories",
            params={"page": page, "per_page": per_page},
        )

    async def get_repository(self, owner: str, repo: str) -> dict:
        return await self.request("GET", f"/repos/{owner}/{repo}")

    async def get_repository_by_id(self, repo_id: str | int) -> dict:
        return await self.request("GET", f"/repositories/{repo_id}")

    async def list_branches(self, owner: str, repo: str, per_page: int = 50) -> list:
        return await self.request(
            "GET",
            f"/repos/{owner}/{repo}/branches",
            params={"per_page": per_page},
        )

    async def list_commits(
        self, owner: str, repo: str, *, sha: str | None = None, per_page: int = 50
    ) -> list:
        params: dict[str, Any] = {"per_page": per_page}
        if sha:
            params["sha"] = sha
        return await self.request("GET", f"/repos/{owner}/{repo}/commits", params=params)

    async def list_pull_requests(
        self, owner: str, repo: str, *, state: str = "all", per_page: int = 30
    ) -> list:
        return await self.request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page, "sort": "updated", "direction": "desc"},
        )

    async def list_issues(
        self, owner: str, repo: str, *, state: str = "all", per_page: int = 30
    ) -> list:
        # GitHub issues endpoint includes PRs; filter later
        return await self.request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page, "sort": "updated", "direction": "desc"},
        )

    async def list_contributors(self, owner: str, repo: str, per_page: int = 30) -> list:
        return await self.request(
            "GET",
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": per_page, "anon": "false"},
        )

    async def get_languages(self, owner: str, repo: str) -> dict:
        return await self.request("GET", f"/repos/{owner}/{repo}/languages")

    async def get_topics(self, owner: str, repo: str) -> dict:
        return await self.request("GET", f"/repos/{owner}/{repo}/topics")

    async def get_readme_metadata(self, owner: str, repo: str) -> dict | None:
        try:
            return await self.request("GET", f"/repos/{owner}/{repo}/readme")
        except GitHubAPIError as exc:
            if exc.status_code == 404:
                return None
            raise


async def fetch_user_profile(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{settings.GITHUB_API_BASE_URL}/user", headers=headers)
        if response.status_code >= 400:
            raise GitHubAPIError("Failed to fetch GitHub user profile", status_code=response.status_code)
        return response.json()


async def list_user_installations(access_token: str) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.GITHUB_API_BASE_URL}/user/installations",
            headers=headers,
            params={"per_page": 100},
        )
        if response.status_code >= 400:
            raise GitHubAPIError(
                "Failed to list user installations", status_code=response.status_code
            )
        data = response.json()
        return data.get("installations", [])
