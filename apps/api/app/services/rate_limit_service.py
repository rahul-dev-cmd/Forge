"""Persist GitHub API rate-limit headers for observability and back-pressure."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.checkpoints import github_rate_limit_repository
from app.utils.logger import logger


class RateLimitService:
    async def record(
        self,
        db: AsyncSession,
        *,
        installation_id: str,
        remaining: int | None,
        limit: int | None,
        reset_epoch: int | None,
        resource: str = "core",
        commit: bool = False,
    ) -> None:
        if remaining is None and limit is None and reset_epoch is None:
            return

        reset_at = None
        if reset_epoch is not None:
            reset_at = datetime.fromtimestamp(reset_epoch, tz=timezone.utc)

        await github_rate_limit_repository.upsert(
            db,
            installation_id=installation_id,
            remaining=int(remaining if remaining is not None else 0),
            limit=int(limit if limit is not None else 5000),
            reset_at=reset_at,
            resource=resource,
        )
        if commit:
            await db.commit()

        if remaining is not None and remaining < 100:
            logger.warning(
                "GitHub rate limit approaching exhaustion",
                extra={
                    "installation_id": installation_id,
                    "remaining": remaining,
                    "limit": limit,
                    "reset_at": reset_at.isoformat() if reset_at else None,
                },
            )

    async def is_exhausted(
        self, db: AsyncSession, installation_id: str, resource: str = "core"
    ) -> bool:
        row = await github_rate_limit_repository.get_for_installation(
            db, installation_id, resource=resource
        )
        if not row:
            return False
        if row.remaining > 0:
            return False
        if row.reset_at and row.reset_at <= datetime.now(timezone.utc):
            return False
        return True


rate_limit_service = RateLimitService()
