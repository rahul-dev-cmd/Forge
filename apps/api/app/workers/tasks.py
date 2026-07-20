"""ARQ worker task definitions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.enums import JobStatus, SyncJobType, SyncStatus
from app.repositories.repository import repository_repository
from app.repositories.sync import repository_sync_repository, webhook_event_repository
from app.services.webhook_service import webhook_service
from app.utils.logger import logger


async def initial_import(ctx: dict, job_id: str) -> dict:
    from app.services.sync_engine import sync_engine
    logger.info("Worker: initial_import", extra={"job_id": job_id})
    async with SessionLocal() as db:
        job = await sync_engine.run_sync_job(db, uuid.UUID(job_id))
        return {"job_id": job_id, "status": job.status}


async def repository_sync(ctx: dict, job_id: str) -> dict:
    from app.services.sync_engine import sync_engine
    logger.info("Worker: repository_sync", extra={"job_id": job_id})
    async with SessionLocal() as db:
        job = await sync_engine.run_sync_job(db, uuid.UUID(job_id))
        return {"job_id": job_id, "status": job.status}



async def process_webhook(ctx: dict, event_id: str) -> dict:
    logger.info("Worker: process_webhook", extra={"event_id": event_id})
    async with SessionLocal() as db:
        event = await webhook_service.process_event(db, uuid.UUID(event_id))
        return {"event_id": event_id, "status": event.status}


async def retry_failed_jobs(ctx: dict) -> dict:
    """Re-queue failed sync jobs and webhook events that still have retries left."""
    from app.workers.queues import enqueue_sync

    retried_sync = 0
    retried_webhooks = 0
    async with SessionLocal() as db:
        jobs = await repository_sync_repository.list_failed_retryable(db)
        for job in jobs:
            job.status = JobStatus.QUEUED.value
            job.error_message = None
            db.add(job)
            await db.commit()
            fn = (
                "initial_import"
                if job.job_type == SyncJobType.INITIAL_IMPORT.value
                else "repository_sync"
            )
            await enqueue_sync(fn, str(job.id))
            retried_sync += 1

        events = await webhook_event_repository.list_failed_retryable(db)
        for event in events:
            await enqueue_sync("process_webhook", str(event.id))
            retried_webhooks += 1

    logger.info(
        "Retry failed jobs complete",
        extra={"sync": retried_sync, "webhooks": retried_webhooks},
    )
    return {"retried_sync": retried_sync, "retried_webhooks": retried_webhooks}


async def periodic_sync(ctx: dict) -> dict:
    """Enqueue syncs for repositories with auto_sync enabled."""
    from app.workers.queues import enqueue_sync

    queued = 0
    async with SessionLocal() as db:
        repos = await repository_repository.list_auto_sync_due(db, limit=50)
        for repo in repos:
            if repo.sync_status == SyncStatus.SYNCING.value:
                continue
            job = await sync_engine.create_sync_job(
                db,
                repository_id=repo.id,
                job_type=SyncJobType.PERIODIC_SYNC,
                installation_id=repo.installation_id,
            )
            await enqueue_sync("repository_sync", str(job.id))
            queued += 1
    logger.info("Periodic sync enqueued", extra={"queued": queued})
    return {"queued": queued}


async def cleanup(ctx: dict) -> dict:
    """Mark stale running jobs as failed and prune old completed webhook noise."""
    marked = 0
    async with SessionLocal() as db:
        stale = await repository_sync_repository.list_stale_running(db, older_than_minutes=90)
        for job in stale:
            job.status = JobStatus.FAILED.value
            job.error_message = "Job timed out (stale running state)"
            job.error_code = "job_timeout"
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            if job.repository_id:
                repo = await repository_repository.get(db, job.repository_id)
                if repo and repo.sync_status == SyncStatus.SYNCING.value:
                    repo.sync_status = SyncStatus.FAILED.value
                    repo.sync_error = job.error_message
                    db.add(repo)
            marked += 1
        await db.commit()
    logger.info("Cleanup complete", extra={"stale_jobs_marked": marked})
    return {"stale_jobs_marked": marked}


# --- Placeholder tasks for index_queue / ai_queue (Milestone 7+) ---


async def prepare_indexing(ctx: dict, repository_id: str, sync_job_id: str | None = None) -> dict:
    """
    Placeholder: enqueue target for future AI indexing pipeline.
    Subscribed via RepositorySynced domain event — no-op body for now.
    """
    logger.info(
        "Placeholder prepare_indexing (index_queue)",
        extra={"repository_id": repository_id, "sync_job_id": sync_job_id},
    )
    return {
        "repository_id": repository_id,
        "sync_job_id": sync_job_id,
        "status": "accepted_placeholder",
    }


async def ai_placeholder(ctx: dict, *args, **kwargs) -> dict:
    """Placeholder consumer for ai_queue."""
    logger.info("Placeholder ai_queue job", extra={"args": args, "kwargs": kwargs})
    return {"status": "accepted_placeholder"}
