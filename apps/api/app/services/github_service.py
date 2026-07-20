"""GitHub App connect / install / import orchestration."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.integrations.github.app_auth import (
    build_install_url,
    build_oauth_authorize_url,
    exchange_oauth_code,
    is_github_app_configured,
    GitHubAppAuthError,
)
from app.integrations.github.client import (
    GitHubClient,
    GitHubAPIError,
    fetch_user_profile,
    list_user_installations,
)
from app.models.enums import (
    InstallationStatus,
    ConnectionStatus,
    SyncStatus,
    SyncJobType,
    RepositoryProvider,
    RepositoryVisibility,
)
from app.models.github import GitHubInstallation, GitHubAccountLink
from app.models.repository import Repository, RepositorySettings
from app.models.audit_log import AuditLog
from app.repositories.github import (
    github_installation_repository,
    github_account_link_repository,
)
from app.repositories.repository import repository_repository
from app.services.sync_engine import sync_engine
from app.utils.encryption import encrypt_value
from app.utils.logger import logger


class GitHubConnectRequest(BaseModel):
    workspace_id: uuid.UUID | None = None
    redirect_after: str | None = None


class GitHubInstallRequest(BaseModel):
    workspace_id: uuid.UUID | None = None
    installation_id: str | None = None


class RepositoryImportRequest(BaseModel):
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    installation_id: str
    provider_repository_id: str
    full_name: str | None = None
    name: str | None = None
    owner: str | None = None
    default_branch: str | None = "main"
    clone_url: str | None = None
    html_url: str | None = None
    private: bool = True


def _serialize_installation(inst: GitHubInstallation) -> dict[str, Any]:
    return {
        "id": str(inst.id),
        "installation_id": inst.installation_id,
        "account_login": inst.account_login,
        "account_id": inst.account_id,
        "account_type": inst.account_type,
        "account_avatar_url": inst.account_avatar_url,
        "status": inst.status,
        "workspace_id": str(inst.workspace_id) if inst.workspace_id else None,
        "last_validated_at": inst.last_validated_at.isoformat() if inst.last_validated_at else None,
        "created_at": inst.created_at.isoformat() if inst.created_at else None,
    }


def serialize_repository(repo: Repository) -> dict[str, Any]:
    return {
        "id": str(repo.id),
        "project_id": str(repo.project_id),
        "workspace_id": str(repo.workspace_id),
        "provider": repo.provider,
        "external_id": repo.external_id,
        "provider_repository_id": repo.provider_repository_id,
        "installation_id": repo.installation_id,
        "name": repo.name,
        "owner": repo.owner,
        "full_name": repo.full_name,
        "description": repo.description,
        "default_branch": repo.default_branch,
        "clone_url": repo.clone_url,
        "html_url": repo.html_url,
        "visibility": repo.visibility,
        "connection_status": repo.connection_status,
        "sync_status": repo.sync_status,
        "sync_error": repo.sync_error,
        "last_synced_at": repo.last_synced_at.isoformat() if repo.last_synced_at else None,
        "stars_count": repo.stars_count,
        "forks_count": repo.forks_count,
        "watchers_count": repo.watchers_count,
        "open_issues_count": repo.open_issues_count,
        "license": repo.license,
        "primary_language": repo.primary_language,
        "readme_exists": repo.readme_exists,
        "indexing_ready": repo.indexing_ready,
        "supports_ai": repo.supports_ai,
        "supports_indexing": repo.supports_indexing,
        "supports_pr_review": repo.supports_pr_review,
        "supports_chat": repo.supports_chat,
        "is_archived": repo.is_archived,
        "is_fork": repo.is_fork,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
    }


class GitHubService:
    def start_connect(self, *, user_id: uuid.UUID, body: GitHubConnectRequest) -> dict[str, Any]:
        """
        Begin OAuth account linking for GitHub App user-to-server flow.
        """
        state = secrets.token_urlsafe(24)
        if not settings.GITHUB_APP_CLIENT_ID:
            # Still return install URL path for App installation-first flows
            return {
                "mode": "install",
                "authorize_url": build_install_url(state=state),
                "install_url": build_install_url(state=state),
                "state": state,
                "configured": is_github_app_configured(),
                "workspace_id": str(body.workspace_id) if body.workspace_id else None,
            }
        return {
            "mode": "oauth",
            "authorize_url": build_oauth_authorize_url(state),
            "install_url": build_install_url(state=state),
            "state": state,
            "configured": is_github_app_configured(),
            "workspace_id": str(body.workspace_id) if body.workspace_id else None,
        }

    def start_install(self, *, body: GitHubInstallRequest) -> dict[str, Any]:
        state = secrets.token_urlsafe(24)
        url = build_install_url(state=state)
        if body.installation_id:
            # Deep-link to existing installation settings / accept
            url = f"{settings.GITHUB_APP_URL.rstrip('/')}/{settings.GITHUB_APP_SLUG}/installations/{body.installation_id}"
        return {
            "install_url": url,
            "state": state,
            "configured": is_github_app_configured(),
            "workspace_id": str(body.workspace_id) if body.workspace_id else None,
        }

    async def complete_oauth_callback(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        code: str,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        try:
            token_data = await exchange_oauth_code(code)
        except GitHubAppAuthError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access_token returned from GitHub")

        profile = await fetch_user_profile(access_token)
        expires_in = token_data.get("expires_in")
        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

        link = await github_account_link_repository.get_by_user(db, user_id)
        if not link:
            link = GitHubAccountLink(
                user_id=user_id,
                github_user_id=str(profile["id"]),
                github_login=profile["login"],
            )
            db.add(link)

        link.github_user_id = str(profile["id"])
        link.github_login = profile["login"]
        link.avatar_url = profile.get("avatar_url")
        link.encrypted_access_token = encrypt_value(access_token)
        if token_data.get("refresh_token"):
            link.encrypted_refresh_token = encrypt_value(token_data["refresh_token"])
        link.token_expires_at = expires_at
        link.scopes = token_data.get("scope")
        link.is_active = True
        await db.commit()
        await db.refresh(link)

        # Sync installations visible to this user
        installations_synced = await self.sync_user_installations(
            db, user_id=user_id, access_token=access_token, workspace_id=workspace_id
        )

        db.add(
            AuditLog(
                actor_id=user_id,
                action="github_connected",
                target_type="github_account_link",
                target_id=link.id,
                details={"github_login": link.github_login, "installations": installations_synced},
            )
        )
        await db.commit()

        return {
            "linked": True,
            "github_login": link.github_login,
            "github_user_id": link.github_user_id,
            "installations_synced": installations_synced,
        }

    async def sync_user_installations(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        access_token: str,
        workspace_id: uuid.UUID | None = None,
    ) -> int:
        try:
            installations = await list_user_installations(access_token)
        except GitHubAPIError as exc:
            logger.warning("Unable to list installations: %s", exc)
            return 0

        count = 0
        for item in installations:
            await self.upsert_installation(
                db,
                user_id=user_id,
                installation_payload=item,
                workspace_id=workspace_id,
            )
            count += 1
        await db.commit()
        return count

    async def upsert_installation(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        installation_payload: dict[str, Any],
        workspace_id: uuid.UUID | None = None,
        encrypted_user_token: str | None = None,
    ) -> GitHubInstallation:
        installation_id = str(installation_payload["id"])
        account = installation_payload.get("account") or {}
        existing = await github_installation_repository.get_by_installation_id(
            db, installation_id
        )
        status_value = InstallationStatus.ACTIVE.value
        if installation_payload.get("suspended_at"):
            status_value = InstallationStatus.SUSPENDED.value

        if existing:
            existing.account_login = account.get("login") or existing.account_login
            existing.account_id = str(account.get("id") or existing.account_id)
            existing.account_type = account.get("type") or existing.account_type
            existing.account_avatar_url = account.get("avatar_url")
            existing.status = status_value
            existing.suspended_at = None
            if installation_payload.get("suspended_at"):
                existing.suspended_at = datetime.now(timezone.utc)
            if workspace_id:
                existing.workspace_id = workspace_id
            if encrypted_user_token:
                existing.encrypted_user_token = encrypted_user_token
            existing.last_validated_at = datetime.now(timezone.utc)
            existing.permissions = str(installation_payload.get("permissions") or "")
            db.add(existing)
            return existing

        inst = GitHubInstallation(
            user_id=user_id,
            workspace_id=workspace_id,
            installation_id=installation_id,
            account_login=account.get("login") or "unknown",
            account_id=str(account.get("id") or "0"),
            account_type=account.get("type") or "Organization",
            account_avatar_url=account.get("avatar_url"),
            status=status_value,
            permissions=str(installation_payload.get("permissions") or ""),
            events=str(installation_payload.get("events") or ""),
            encrypted_user_token=encrypted_user_token,
            last_validated_at=datetime.now(timezone.utc),
        )
        db.add(inst)
        await db.flush()
        return inst

    async def register_installation(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        installation_id: str,
        workspace_id: uuid.UUID | None = None,
    ) -> GitHubInstallation:
        """
        After GitHub App install redirect, fetch installation details and persist.
        """
        if is_github_app_configured():
            try:
                client = GitHubClient(installation_id)
                payload = await client.get_installation()
            except (GitHubAPIError, GitHubAppAuthError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
                ) from exc
        else:
            # Dev stub when App credentials are absent
            payload = {
                "id": int(installation_id) if installation_id.isdigit() else hash(installation_id) % 10_000_000,
                "account": {
                    "login": f"dev-account-{installation_id}",
                    "id": 1,
                    "type": "Organization",
                    "avatar_url": None,
                },
                "permissions": {},
                "events": [],
            }

        inst = await self.upsert_installation(
            db,
            user_id=user_id,
            installation_payload=payload,
            workspace_id=workspace_id,
        )
        await db.commit()
        await db.refresh(inst)
        return inst

    async def list_installations(
        self, db: AsyncSession, *, user_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        items = await github_installation_repository.list_for_user(db, user_id)
        return [_serialize_installation(i) for i in items]

    async def list_available_repositories(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        installation_id: str | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> dict[str, Any]:
        installations = await github_installation_repository.list_for_user(db, user_id)
        if installation_id:
            installations = [i for i in installations if i.installation_id == installation_id]
        if not installations:
            return {"items": [], "total_count": 0, "page": page}

        if not is_github_app_configured():
            # Dev: return empty remote list; import still works with explicit payload
            return {
                "items": [],
                "total_count": 0,
                "page": page,
                "message": "GitHub App not configured — provide repository details on import.",
            }

        all_repos: list[dict[str, Any]] = []
        total = 0
        for inst in installations:
            if inst.status != InstallationStatus.ACTIVE.value:
                continue
            try:
                client = GitHubClient(inst.installation_id)
                data = await client.list_installation_repositories(page=page, per_page=per_page)
            except (GitHubAPIError, GitHubAppAuthError) as exc:
                logger.warning(
                    "Failed listing repos for installation %s: %s",
                    inst.installation_id,
                    exc,
                )
                continue
            total += int(data.get("total_count") or 0)
            for repo in data.get("repositories") or []:
                existing = await repository_repository.get_by_provider_repository_id(
                    db, str(repo["id"])
                )
                all_repos.append(
                    {
                        "provider_repository_id": str(repo["id"]),
                        "installation_id": inst.installation_id,
                        "name": repo.get("name"),
                        "full_name": repo.get("full_name"),
                        "owner": (repo.get("owner") or {}).get("login"),
                        "private": bool(repo.get("private")),
                        "default_branch": repo.get("default_branch") or "main",
                        "clone_url": repo.get("clone_url"),
                        "html_url": repo.get("html_url"),
                        "description": repo.get("description"),
                        "language": repo.get("language"),
                        "already_imported": existing is not None,
                        "forge_repository_id": str(existing.id) if existing else None,
                    }
                )
        return {"items": all_repos, "total_count": total or len(all_repos), "page": page}

    async def import_repository(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        body: RepositoryImportRequest,
        enqueue_sync: bool = True,
    ) -> dict[str, Any]:
        inst = await github_installation_repository.get_by_installation_id(
            db, body.installation_id
        )
        if not inst or inst.user_id != user_id:
            # Allow if installation exists for another user in same workspace later;
            # for now require ownership.
            if not inst:
                raise HTTPException(
                    status_code=404,
                    detail="GitHub installation not found. Connect GitHub and install the Forge App first.",
                )
            if inst.status != InstallationStatus.ACTIVE.value:
                raise HTTPException(status_code=403, detail=f"Installation status is {inst.status}")

        existing = await repository_repository.get_by_provider_repository_id(
            db, body.provider_repository_id
        )
        if existing and existing.deleted_at is None:
            raise HTTPException(
                status_code=409,
                detail="Repository already imported",
            )

        # Optionally enrich from GitHub
        owner = body.owner
        name = body.name
        full_name = body.full_name
        clone_url = body.clone_url
        html_url = body.html_url
        default_branch = body.default_branch or "main"
        private = body.private
        description = None
        language = None

        if is_github_app_configured():
            try:
                client = GitHubClient(body.installation_id)
                remote = await client.get_repository_by_id(body.provider_repository_id)
                owner = (remote.get("owner") or {}).get("login") or owner
                name = remote.get("name") or name
                full_name = remote.get("full_name") or full_name
                clone_url = remote.get("clone_url") or clone_url
                html_url = remote.get("html_url") or html_url
                default_branch = remote.get("default_branch") or default_branch
                private = bool(remote.get("private"))
                description = remote.get("description")
                language = remote.get("language")
            except (GitHubAPIError, GitHubAppAuthError) as exc:
                if not (owner and name and clone_url):
                    raise HTTPException(status_code=400, detail=str(exc)) from exc

        if not name:
            name = (full_name or "").split("/")[-1] or f"repo-{body.provider_repository_id}"
        if not owner and full_name and "/" in full_name:
            owner = full_name.split("/")[0]
        if not full_name and owner and name:
            full_name = f"{owner}/{name}"
        if not clone_url and full_name:
            clone_url = f"https://github.com/{full_name}.git"
        if not html_url and full_name:
            html_url = f"https://github.com/{full_name}"

        repo = Repository(
            project_id=body.project_id,
            workspace_id=body.workspace_id,
            github_installation_fk=inst.id if inst else None,
            provider=RepositoryProvider.GITHUB.value,
            external_id=body.provider_repository_id,
            provider_repository_id=body.provider_repository_id,
            installation_id=body.installation_id,
            name=name,
            owner=owner,
            full_name=full_name,
            description=description,
            default_branch=default_branch,
            clone_url=clone_url or "",
            html_url=html_url,
            visibility=(
                RepositoryVisibility.PRIVATE.value
                if private
                else RepositoryVisibility.PUBLIC.value
            ),
            connection_status=ConnectionStatus.CONNECTED.value,
            sync_status=SyncStatus.QUEUED.value,
            primary_language=language,
            supports_ai=True,
            supports_indexing=True,
            supports_pr_review=False,
            supports_chat=False,
        )
        db.add(repo)
        await db.flush()

        # Ensure sync checkpoint row exists for incremental syncs
        from app.repositories.checkpoints import sync_checkpoint_repository

        await sync_checkpoint_repository.get_or_create(db, repo.id)

        db.add(
            RepositorySettings(
                repository_id=repo.id,
                ai_enabled=True,
                indexing_enabled=True,
                auto_sync=True,
                sync_interval=3600,
            )
        )
        db.add(
            AuditLog(
                actor_id=user_id,
                action="repository_import",
                target_type="repository",
                target_id=repo.id,
                details={
                    "full_name": full_name,
                    "installation_id": body.installation_id,
                    "provider_repository_id": body.provider_repository_id,
                },
            )
        )
        await db.commit()
        await db.refresh(repo)

        job = await sync_engine.create_sync_job(
            db,
            repository_id=repo.id,
            job_type=SyncJobType.INITIAL_IMPORT,
            triggered_by=user_id,
            installation_id=body.installation_id,
        )

        if enqueue_sync:
            from app.workers.queues import enqueue_sync as enqueue_sync_job

            arq_id = await enqueue_sync_job("initial_import", str(job.id))
            if arq_id:
                job.arq_job_id = arq_id
                await db.commit()

        from app.events.bus import event_bus, RepositoryImported

        await event_bus.publish(
            RepositoryImported(
                repository_id=str(repo.id),
                workspace_id=str(repo.workspace_id),
                project_id=str(repo.project_id),
                installation_id=body.installation_id,
                provider_repository_id=body.provider_repository_id,
                sync_job_id=str(job.id),
            )
        )

        return {
            "repository": serialize_repository(repo),
            "sync_job": {
                "id": str(job.id),
                "status": job.status,
                "job_type": job.job_type,
            },
        }

    async def disconnect_repository(
        self, db: AsyncSession, *, repository_id: uuid.UUID, user_id: uuid.UUID
    ) -> Repository | None:
        repo = await repository_repository.get(db, repository_id)
        if not repo:
            return None
        repo.connection_status = ConnectionStatus.DISCONNECTED.value
        repo.sync_status = SyncStatus.DISCONNECTED.value
        repo.installation_id = None
        repo.github_installation_fk = None
        db.add(repo)
        db.add(
            AuditLog(
                actor_id=user_id,
                action="repository_disconnected",
                target_type="repository",
                target_id=repo.id,
                details={"full_name": repo.full_name},
            )
        )
        await db.commit()
        await db.refresh(repo)
        return repo


github_service = GitHubService()
