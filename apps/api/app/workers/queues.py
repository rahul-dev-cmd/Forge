"""Named ARQ queues — sync work is isolated from future index/AI work."""

from __future__ import annotations

from enum import Enum

from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from app.config.settings import settings
from app.utils.logger import logger


class QueueName(str, Enum):
    SYNC = "sync_queue"
    INDEX = "index_queue"
    AI = "ai_queue"


_pools: dict[str, ArqRedis] = {}


def redis_settings_from_url(url: str) -> RedisSettings:
    return RedisSettings.from_dsn(url)


async def get_queue_pool(queue: QueueName | str) -> ArqRedis | None:
    name = queue.value if isinstance(queue, QueueName) else queue
    if name in _pools:
        return _pools[name]
    try:
        pool = await create_pool(redis_settings_from_url(settings.REDIS_URL))
        _pools[name] = pool
        return pool
    except Exception as exc:
        logger.warning("ARQ pool unavailable for %s: %s", name, exc)
        return None


async def enqueue_to(
    queue: QueueName | str,
    function_name: str,
    *args,
    **kwargs,
) -> str | None:
    """
    Enqueue a job onto a named queue.
    Returns job id, or None if Redis is unavailable (may run sync inline).
    """
    name = queue.value if isinstance(queue, QueueName) else str(queue)
    pool = await get_queue_pool(name)
    if pool is None:
        logger.warning(
            "Skipping enqueue for %s on %s — Redis unavailable",
            function_name,
            name,
        )
        if name == QueueName.SYNC.value and function_name in {
            "initial_import",
            "repository_sync",
            "process_webhook",
        }:
            await _inline_sync_fallback(function_name, *args)
        return None

    job = await pool.enqueue_job(function_name, *args, _queue_name=name, **kwargs)
    return job.job_id if job else None


async def enqueue_sync(function_name: str, *args, **kwargs) -> str | None:
    return await enqueue_to(QueueName.SYNC, function_name, *args, **kwargs)


async def enqueue_index(function_name: str, *args, **kwargs) -> str | None:
    """Placeholder path for future indexing workers."""
    return await enqueue_to(QueueName.INDEX, function_name, *args, **kwargs)


async def enqueue_ai(function_name: str, *args, **kwargs) -> str | None:
    """Placeholder path for future AI workers."""
    return await enqueue_to(QueueName.AI, function_name, *args, **kwargs)


async def _inline_sync_fallback(function_name: str, *args) -> None:
    from app.core.database import SessionLocal
    from app.services.sync_engine import sync_engine
    from app.services.webhook_service import webhook_service
    import uuid

    try:
        async with SessionLocal() as db:
            if function_name in {"initial_import", "repository_sync"} and args:
                await sync_engine.run_sync_job(db, uuid.UUID(str(args[0])))
            elif function_name == "process_webhook" and args:
                await webhook_service.process_event(db, uuid.UUID(str(args[0])))
    except Exception:
        logger.exception("Inline sync fallback failed for %s", function_name)


# Backwards-compatible alias used by older call sites
async def enqueue_job(function_name: str, *args, **kwargs) -> str | None:
    return await enqueue_sync(function_name, *args, **kwargs)
