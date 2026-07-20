from typing import Any, List
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sync import RepositorySync
from app.models.webhook import WebhookEvent
from app.models.enums import JobStatus, WebhookProcessingStatus
from app.repositories.base import BaseRepository


class RepositorySyncRepository(BaseRepository[RepositorySync, Any, Any]):
    def __init__(self):
        super().__init__(RepositorySync)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, *, limit: int = 20
    ) -> List[RepositorySync]:
        result = await db.execute(
            select(RepositorySync)
            .filter(RepositorySync.repository_id == repository_id)
            .order_by(RepositorySync.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_failed_retryable(
        self, db: AsyncSession, *, limit: int = 50
    ) -> List[RepositorySync]:
        result = await db.execute(
            select(RepositorySync)
            .filter(
                and_(
                    RepositorySync.status == JobStatus.FAILED.value,
                    RepositorySync.retry_count < RepositorySync.max_retries,
                )
            )
            .order_by(RepositorySync.updated_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_stale_running(
        self, db: AsyncSession, *, older_than_minutes: int = 60
    ) -> List[RepositorySync]:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=older_than_minutes)
        result = await db.execute(
            select(RepositorySync).filter(
                and_(
                    RepositorySync.status == JobStatus.RUNNING.value,
                    RepositorySync.started_at < cutoff,
                )
            )
        )
        return list(result.scalars().all())


class WebhookEventRepository(BaseRepository[WebhookEvent, Any, Any]):
    def __init__(self):
        super().__init__(WebhookEvent)

    async def get_by_delivery_id(
        self, db: AsyncSession, delivery_id: str
    ) -> WebhookEvent | None:
        result = await db.execute(
            select(WebhookEvent).filter(
                WebhookEvent.webhook_delivery_id == delivery_id
            )
        )
        return result.scalars().first()

    async def list_failed_retryable(
        self, db: AsyncSession, *, limit: int = 50
    ) -> List[WebhookEvent]:
        result = await db.execute(
            select(WebhookEvent)
            .filter(
                and_(
                    WebhookEvent.status == WebhookProcessingStatus.FAILED.value,
                    WebhookEvent.retry_count < 3,
                )
            )
            .order_by(WebhookEvent.updated_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())


repository_sync_repository = RepositorySyncRepository()
webhook_event_repository = WebhookEventRepository()
