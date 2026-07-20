"""Domain event subscribers.

AI indexing can subscribe to RepositorySynced later without changing sync/import code.
"""

from __future__ import annotations

from app.events.bus import (
    event_bus,
    RepositoryImported,
    RepositorySynced,
    SyncCompleted,
    WebhookProcessed,
)
from app.utils.logger import logger
from app.workers.queues import QueueName, enqueue_to


async def on_repository_imported(event: RepositoryImported) -> None:
    logger.info(
        "Handler: RepositoryImported",
        extra={"repository_id": event.repository_id, "sync_job_id": event.sync_job_id},
    )


async def on_repository_synced(event: RepositorySynced) -> None:
    """
    Prepare downstream indexing without coupling sync to AI.
    Placeholder: enqueue a no-op index job when the repo supports indexing.
    """
    logger.info(
        "Handler: RepositorySynced",
        extra={
            "repository_id": event.repository_id,
            "indexing_ready": event.indexing_ready,
            "supports_indexing": event.supports_indexing,
        },
    )
    if event.indexing_ready and event.supports_indexing:
        await enqueue_to(
            QueueName.INDEX,
            "prepare_indexing",
            event.repository_id,
            event.sync_job_id,
        )


async def on_sync_completed(event: SyncCompleted) -> None:
    logger.info(
        "Handler: SyncCompleted",
        extra={
            "repository_id": event.repository_id,
            "last_commit_sha": event.last_commit_sha,
        },
    )


async def on_webhook_processed(event: WebhookProcessed) -> None:
    logger.info(
        "Handler: WebhookProcessed",
        extra={
            "webhook_event_id": event.webhook_event_id,
            "event_type": event.event_type,
            "repository_id": event.repository_id,
        },
    )


def register_event_handlers() -> None:
    """Idempotent registration of built-in subscribers."""
    event_bus.subscribe(RepositoryImported, on_repository_imported)
    event_bus.subscribe(RepositorySynced, on_repository_synced)
    event_bus.subscribe(SyncCompleted, on_sync_completed)
    event_bus.subscribe(WebhookProcessed, on_webhook_processed)
