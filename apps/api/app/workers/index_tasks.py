"""ARQ worker tasks for Milestone 7 Code Intelligence & Indexing (index_queue)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.code_intelligence import IndexJob
from app.models.enums import IndexJobType, IndexStatus
from app.repositories.repository import repository_repository
from app.services.indexing_engine import indexing_engine
from app.services.storage_manager import storage_manager
from app.utils.logger import logger


async def repository_clone(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: repository_clone", extra={"repository_id": repository_id})
    async with SessionLocal() as db:
        repo = await repository_repository.get(db, uuid.UUID(repository_id))
        if not repo:
            return {"status": "error", "message": "Repository not found"}
        storage_manager.clone_repository(uuid.UUID(repository_id), repo.clone_url)
        return {"repository_id": repository_id, "status": "cloned"}


async def repository_pull(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: repository_pull", extra={"repository_id": repository_id})
    storage_manager.pull_repository(uuid.UUID(repository_id))
    return {"repository_id": repository_id, "status": "pulled"}


async def repository_index(ctx: dict, repository_id: str, job_id: str | None = None) -> dict:
    logger.info("Worker: repository_index", extra={"repository_id": repository_id, "job_id": job_id})
    async with SessionLocal() as db:
        j_id = uuid.UUID(job_id) if job_id else None
        idx = await indexing_engine.run_indexing_pipeline(db, uuid.UUID(repository_id), job_id=j_id)
        return {"repository_id": repository_id, "index_id": str(idx.id), "status": idx.status}


async def incremental_index(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: incremental_index", extra={"repository_id": repository_id})
    return await repository_index(ctx, repository_id)


async def cleanup_index(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: cleanup_index", extra={"repository_id": repository_id})
    removed = storage_manager.delete_repository_storage(uuid.UUID(repository_id))
    return {"repository_id": repository_id, "storage_removed": removed}


async def reindex_repository(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: reindex_repository", extra={"repository_id": repository_id})
    storage_manager.delete_repository_storage(uuid.UUID(repository_id))
    return await repository_index(ctx, repository_id)


async def cancel_index(ctx: dict, job_id: str) -> dict:
    logger.info("Worker: cancel_index", extra={"job_id": job_id})
    async with SessionLocal() as db:
        j_res = await db.execute(select(IndexJob).filter(IndexJob.id == uuid.UUID(job_id)))
        job = j_res.scalars().first()
        if job:
            job.status = IndexStatus.CANCELLED.value
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()
            return {"job_id": job_id, "status": "cancelled"}
    return {"job_id": job_id, "status": "not_found"}


async def retry_failed_index(ctx: dict) -> dict:
    """Retry failed index jobs with status = FAILED."""
    from app.workers.queues import enqueue_index

    retried = 0
    async with SessionLocal() as db:
        res = await db.execute(select(IndexJob).filter(IndexJob.status == IndexStatus.FAILED.value).limit(10))
        failed_jobs = list(res.scalars().all())
        for job in failed_jobs:
            job.status = IndexStatus.QUEUED.value
            job.error_message = None
            db.add(job)
            await db.commit()
            await enqueue_index("repository_index", str(job.repository_id), str(job.id))
            retried += 1

    return {"retried": retried}
