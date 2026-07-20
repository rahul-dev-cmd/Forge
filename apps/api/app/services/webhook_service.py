"""Webhook ingestion and processing service."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.github.webhooks import (
    SUPPORTED_EVENTS,
    verify_webhook_signature,
    parse_webhook_payload,
    extract_installation_id,
    extract_repository_id,
)
from app.models.enums import (
    WebhookProcessingStatus,
    InstallationStatus,
    SyncJobType,
    SyncStatus,
    ConnectionStatus,
)
from app.models.webhook import WebhookEvent
from app.repositories.sync import webhook_event_repository
from app.repositories.github import github_installation_repository
from app.repositories.repository import repository_repository
from app.services.sync_engine import sync_engine
from app.utils.logger import logger


class WebhookService:
    async def ingest(
        self,
        db: AsyncSession,
        *,
        delivery_id: str,
        event_type: str,
        signature_header: str | None,
        payload_body: bytes,
    ) -> dict[str, Any]:
        signature_valid = verify_webhook_signature(payload_body, signature_header)
        if not signature_valid:
            logger.warning(
                "Invalid webhook signature",
                extra={"delivery_id": delivery_id, "event_type": event_type},
            )
            return {"accepted": False, "reason": "invalid_signature"}

        existing = await webhook_event_repository.get_by_delivery_id(db, delivery_id)
        if existing:
            return {"accepted": True, "duplicate": True, "id": str(existing.id)}

        payload = parse_webhook_payload(payload_body)
        installation_id = extract_installation_id(payload)
        provider_repo_id = extract_repository_id(payload)
        action = payload.get("action")

        repository_id = None
        if provider_repo_id:
            repo = await repository_repository.get_by_provider_repository_id(
                db, provider_repo_id
            )
            if repo:
                repository_id = repo.id
                repo.last_webhook_delivery_id = delivery_id
                db.add(repo)

        event = WebhookEvent(
            webhook_delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            installation_id=installation_id,
            provider_repository_id=provider_repo_id,
            repository_id=repository_id,
            payload=payload_body.decode("utf-8"),
            signature_valid=True,
            status=WebhookProcessingStatus.RECEIVED.value,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        if event_type not in SUPPORTED_EVENTS:
            event.status = WebhookProcessingStatus.IGNORED.value
            event.processed_at = datetime.now(timezone.utc)
            await db.commit()
            return {"accepted": True, "ignored": True, "id": str(event.id)}

        event.status = WebhookProcessingStatus.QUEUED.value
        await db.commit()

        from app.workers.queues import enqueue_sync

        arq_id = await enqueue_sync("process_webhook", str(event.id))
        if arq_id:
            event.arq_job_id = arq_id
            await db.commit()

        return {"accepted": True, "id": str(event.id), "queued": True}

    async def process_event(self, db: AsyncSession, event_id: uuid.UUID) -> WebhookEvent:
        event = await webhook_event_repository.get(db, event_id)
        if not event:
            raise ValueError(f"Webhook event {event_id} not found")

        event.status = WebhookProcessingStatus.PROCESSING.value
        await db.commit()

        try:
            payload = json.loads(event.payload)
            await self._dispatch(db, event, payload)
            event.status = WebhookProcessingStatus.COMPLETED.value
            event.processed_at = datetime.now(timezone.utc)
            event.error_message = None

            if event.repository_id and event.webhook_delivery_id:
                from app.repositories.checkpoints import sync_checkpoint_repository

                await sync_checkpoint_repository.update_checkpoint(
                    db,
                    event.repository_id,
                    last_webhook_delivery=event.webhook_delivery_id,
                )

            await db.commit()
            await db.refresh(event)

            from app.events.bus import event_bus, WebhookProcessed

            await event_bus.publish(
                WebhookProcessed(
                    webhook_event_id=str(event.id),
                    event_type=event.event_type,
                    action=event.action,
                    repository_id=str(event.repository_id) if event.repository_id else None,
                    installation_id=event.installation_id,
                )
            )
            return event
        except Exception as exc:
            event.status = WebhookProcessingStatus.FAILED.value
            event.error_message = str(exc)
            event.retry_count = (event.retry_count or 0) + 1
            await db.commit()
            await db.refresh(event)
            logger.exception("Webhook processing failed", extra={"event_id": str(event_id)})
            return event

    async def _dispatch(
        self, db: AsyncSession, event: WebhookEvent, payload: dict[str, Any]
    ) -> None:
        et = event.event_type
        action = event.action

        if et == "ping":
            return

        if et == "installation":
            await self._handle_installation(db, action, payload)
            return

        if et == "installation_repositories":
            # Repos added/removed from installation — sync affected repos if imported
            if event.repository_id:
                await self._queue_repo_sync(db, event.repository_id, event.installation_id)
            return

        if et == "repository":
            await self._handle_repository_event(db, action, payload, event)
            return

        # Metadata-changing events → incremental sync
        if et in {"push", "pull_request", "issues", "create", "delete", "release"}:
            if event.repository_id:
                await self._queue_repo_sync(db, event.repository_id, event.installation_id)
            return

    async def _handle_installation(
        self, db: AsyncSession, action: str | None, payload: dict[str, Any]
    ) -> None:
        installation = payload.get("installation") or {}
        installation_id = str(installation.get("id") or "")
        if not installation_id:
            return
        existing = await github_installation_repository.get_by_installation_id(
            db, installation_id
        )
        if not existing:
            return

        if action in {"deleted", "revoke"}:
            existing.status = InstallationStatus.DELETED.value
        elif action == "suspend":
            existing.status = InstallationStatus.SUSPENDED.value
            existing.suspended_at = datetime.now(timezone.utc)
        elif action in {"unsuspend", "created", "new_permissions_accepted"}:
            existing.status = InstallationStatus.ACTIVE.value
            existing.suspended_at = None
            existing.last_validated_at = datetime.now(timezone.utc)
        db.add(existing)

        # Mark linked repositories
        from sqlalchemy import select
        from app.models.repository import Repository

        result = await db.execute(
            select(Repository).filter(Repository.installation_id == installation_id)
        )
        for repo in result.scalars().all():
            if action in {"deleted", "revoke"}:
                repo.connection_status = ConnectionStatus.DISCONNECTED.value
                repo.sync_status = SyncStatus.DISCONNECTED.value
                repo.sync_error = "GitHub App installation deleted or permissions revoked"
            elif action == "suspend":
                repo.connection_status = ConnectionStatus.EXPIRED.value
                repo.sync_error = "GitHub App installation suspended"
            db.add(repo)
        await db.commit()

    async def _handle_repository_event(
        self,
        db: AsyncSession,
        action: str | None,
        payload: dict[str, Any],
        event: WebhookEvent,
    ) -> None:
        if not event.repository_id:
            return
        repo = await repository_repository.get(db, event.repository_id)
        if not repo:
            return

        if action == "deleted":
            repo.connection_status = ConnectionStatus.ERROR.value
            repo.sync_status = SyncStatus.FAILED.value
            repo.sync_error = "Repository deleted on GitHub"
            db.add(repo)
            await db.commit()
            return

        if action == "transferred":
            remote = payload.get("repository") or {}
            repo.owner = (remote.get("owner") or {}).get("login") or repo.owner
            repo.full_name = remote.get("full_name") or repo.full_name
            repo.html_url = remote.get("html_url") or repo.html_url
            repo.clone_url = remote.get("clone_url") or repo.clone_url
            repo.sync_error = "Repository transferred — metadata updated"
            db.add(repo)
            await db.commit()
            await self._queue_repo_sync(db, repo.id, event.installation_id)
            return

        if action in {"renamed", "edited", "privatized", "publicized", "archived", "unarchived"}:
            await self._queue_repo_sync(db, repo.id, event.installation_id)

    async def _queue_repo_sync(
        self,
        db: AsyncSession,
        repository_id: uuid.UUID,
        installation_id: str | None,
    ) -> None:
        job = await sync_engine.create_sync_job(
            db,
            repository_id=repository_id,
            job_type=SyncJobType.WEBHOOK_PROCESSING,
            installation_id=installation_id,
        )
        from app.workers.queues import enqueue_sync

        arq_id = await enqueue_sync("repository_sync", str(job.id))
        if arq_id:
            job.arq_job_id = arq_id
            await db.commit()


webhook_service = WebhookService()
