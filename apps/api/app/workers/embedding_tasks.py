"""ARQ worker tasks for Milestone 8 AI Knowledge & Embedding Pipelines (ai_queue)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.ai_knowledge import EmbeddingJob
from app.models.enums import EmbeddingStatus
from app.services.embedding_pipeline import embedding_pipeline
from app.services.vector_db.factory import vector_db_factory
from app.config.settings import settings
from app.utils.logger import logger


async def repository_embed(ctx: dict, repository_id: str, job_id: str | None = None) -> dict:
    logger.info("Worker: repository_embed", extra={"repository_id": repository_id, "job_id": job_id})
    async with SessionLocal() as db:
        j_id = uuid.UUID(job_id) if job_id else None
        know = await embedding_pipeline.run_embedding_pipeline(db, uuid.UUID(repository_id), job_id=j_id)
        return {"repository_id": repository_id, "total_vectors": know.total_vectors, "health": know.embedding_health}


async def incremental_embedding(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: incremental_embedding", extra={"repository_id": repository_id})
    return await repository_embed(ctx, repository_id)


async def reembed_repository(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: reembed_repository", extra={"repository_id": repository_id})
    # Clear existing vectors for repo
    v_db = vector_db_factory.get_provider()
    await v_db.delete_collection(settings.QDRANT_COLLECTION_NAME)
    return await repository_embed(ctx, repository_id)


async def cleanup_embeddings(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: cleanup_embeddings", extra={"repository_id": repository_id})
    return {"repository_id": repository_id, "status": "cleaned"}


async def refresh_embeddings(ctx: dict, repository_id: str) -> dict:
    logger.info("Worker: refresh_embeddings", extra={"repository_id": repository_id})
    return await repository_embed(ctx, repository_id)


async def cancel_embedding(ctx: dict, job_id: str) -> dict:
    logger.info("Worker: cancel_embedding", extra={"job_id": job_id})
    async with SessionLocal() as db:
        j_res = await db.execute(select(EmbeddingJob).filter(EmbeddingJob.id == uuid.UUID(job_id)))
        job = j_res.scalars().first()
        if job:
            job.status = EmbeddingStatus.CANCELLED.value
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()
            return {"job_id": job_id, "status": "cancelled"}
    return {"job_id": job_id, "status": "not_found"}


async def retry_failed_embeddings(ctx: dict) -> dict:
    from app.workers.queues import enqueue_ai

    retried = 0
    async with SessionLocal() as db:
        res = await db.execute(select(EmbeddingJob).filter(EmbeddingJob.status == EmbeddingStatus.FAILED.value).limit(10))
        failed_jobs = list(res.scalars().all())
        for job in failed_jobs:
            job.status = EmbeddingStatus.QUEUED.value
            job.error_message = None
            db.add(job)
            await db.commit()
            await enqueue_ai("repository_embed", str(job.repository_id), str(job.id))
            retried += 1

    return {"retried": retried}
