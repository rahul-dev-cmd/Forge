from typing import Any
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoints import RepositorySyncCheckpoint, GitHubRateLimit
from app.repositories.base import BaseRepository


class SyncCheckpointRepository(BaseRepository[RepositorySyncCheckpoint, Any, Any]):
    def __init__(self):
        super().__init__(RepositorySyncCheckpoint)

    async def get_by_repository(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> RepositorySyncCheckpoint | None:
        result = await db.execute(
            select(RepositorySyncCheckpoint).filter(
                RepositorySyncCheckpoint.repository_id == repository_id
            )
        )
        return result.scalars().first()

    async def get_or_create(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> RepositorySyncCheckpoint:
        existing = await self.get_by_repository(db, repository_id)
        if existing:
            return existing
        row = RepositorySyncCheckpoint(repository_id=repository_id)
        db.add(row)
        await db.flush()
        return row

    async def update_checkpoint(
        self,
        db: AsyncSession,
        repository_id: uuid.UUID,
        *,
        last_commit_sha: str | None = None,
        last_webhook_delivery: str | None = None,
        last_sync_cursor: str | None = None,
    ) -> RepositorySyncCheckpoint:
        row = await self.get_or_create(db, repository_id)
        if last_commit_sha is not None:
            row.last_commit_sha = last_commit_sha
        if last_webhook_delivery is not None:
            row.last_webhook_delivery = last_webhook_delivery
        if last_sync_cursor is not None:
            row.last_sync_cursor = last_sync_cursor
        row.last_synced_at = datetime.now(timezone.utc)
        db.add(row)
        return row


class GitHubRateLimitRepository(BaseRepository[GitHubRateLimit, Any, Any]):
    def __init__(self):
        super().__init__(GitHubRateLimit)

    async def upsert(
        self,
        db: AsyncSession,
        *,
        installation_id: str,
        remaining: int,
        limit: int,
        reset_at: datetime | None,
        resource: str = "core",
    ) -> GitHubRateLimit:
        result = await db.execute(
            select(GitHubRateLimit).filter(
                GitHubRateLimit.installation_id == installation_id,
                GitHubRateLimit.resource == resource,
            )
        )
        row = result.scalars().first()
        now = datetime.now(timezone.utc)
        if row:
            row.remaining = remaining
            row.limit = limit
            row.reset_at = reset_at
            row.observed_at = now
            db.add(row)
            return row
        row = GitHubRateLimit(
            installation_id=installation_id,
            resource=resource,
            remaining=remaining,
            limit=limit,
            reset_at=reset_at,
            observed_at=now,
        )
        db.add(row)
        return row

    async def get_for_installation(
        self, db: AsyncSession, installation_id: str, resource: str = "core"
    ) -> GitHubRateLimit | None:
        result = await db.execute(
            select(GitHubRateLimit).filter(
                GitHubRateLimit.installation_id == installation_id,
                GitHubRateLimit.resource == resource,
            )
        )
        return result.scalars().first()


sync_checkpoint_repository = SyncCheckpointRepository()
github_rate_limit_repository = GitHubRateLimitRepository()
