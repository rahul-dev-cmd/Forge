"""ARQ worker entrypoints — one process per named queue.

Run sync worker (default):
  arq app.workers.settings.WorkerSettings

Placeholder index / AI workers (ready for Milestone 7+):
  arq app.workers.settings.IndexWorkerSettings
  arq app.workers.settings.AIWorkerSettings
"""

from __future__ import annotations

from arq import cron

from app.config.settings import settings
from app.workers.queues import QueueName, redis_settings_from_url
from app.workers.tasks import (
    initial_import,
    repository_sync,
    process_webhook,
    retry_failed_jobs,
    periodic_sync,
    cleanup,
    prepare_indexing,
    ai_placeholder,
)


class WorkerSettings:
    """Consumes sync_queue — repository import, sync, webhooks, maintenance."""

    functions = [
        initial_import,
        repository_sync,
        process_webhook,
        retry_failed_jobs,
        periodic_sync,
        cleanup,
    ]
    queue_name = QueueName.SYNC.value
    redis_settings = redis_settings_from_url(settings.REDIS_URL)
    cron_jobs = [
        cron(retry_failed_jobs, minute={0, 15, 30, 45}),
        cron(periodic_sync, minute={5}),
        cron(cleanup, hour={3}, minute={0}),
    ]
    max_jobs = 10
    job_timeout = 600


from app.workers.index_tasks import (
    repository_clone,
    repository_pull,
    repository_index,
    incremental_index,
    cleanup_index,
    reindex_repository,
    cancel_index,
    retry_failed_index,
)


class IndexWorkerSettings:
    """Consumes index_queue — repository cloning, AST parsing, symbol extraction."""

    functions = [
        prepare_indexing,
        repository_clone,
        repository_pull,
        repository_index,
        incremental_index,
        cleanup_index,
        reindex_repository,
        cancel_index,
        retry_failed_index,
    ]
    queue_name = QueueName.INDEX.value
    redis_settings = redis_settings_from_url(settings.REDIS_URL)
    cron_jobs = [
        cron(retry_failed_index, minute={10, 40}),
    ]
    max_jobs = 5
    job_timeout = 900



from app.workers.embedding_tasks import (
    repository_embed,
    incremental_embedding,
    reembed_repository,
    cleanup_embeddings,
    refresh_embeddings,
    cancel_embedding,
    retry_failed_embeddings,
)


class AIWorkerSettings:
    """Consumes ai_queue — vector embedding generation, RAG context preparation."""

    functions = [
        ai_placeholder,
        repository_embed,
        incremental_embedding,
        reembed_repository,
        cleanup_embeddings,
        refresh_embeddings,
        cancel_embedding,
        retry_failed_embeddings,
    ]
    queue_name = QueueName.AI.value
    redis_settings = redis_settings_from_url(settings.REDIS_URL)
    cron_jobs = [
        cron(retry_failed_embeddings, minute={20, 50}),
    ]
    max_jobs = 5
    job_timeout = 900

