"""Lightweight in-process domain event bus.

Services publish events; subscribers react without tight coupling.
Future AI indexing can subscribe to RepositorySynced without changing sync code.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar
import uuid

from app.utils.logger import logger

E = TypeVar("E", bound="DomainEvent")
Handler = Callable[[Any], Awaitable[None] | None]


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base domain event. Subclasses add typed payload fields."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RepositoryImported(DomainEvent):
    repository_id: str = ""
    workspace_id: str = ""
    project_id: str = ""
    installation_id: str | None = None
    provider_repository_id: str | None = None
    sync_job_id: str | None = None


@dataclass(frozen=True, slots=True)
class RepositorySynced(DomainEvent):
    repository_id: str = ""
    sync_job_id: str = ""
    job_type: str = ""
    commits_synced: int = 0
    indexing_ready: bool = False
    supports_indexing: bool = False


@dataclass(frozen=True, slots=True)
class SyncCompleted(DomainEvent):
    """Emitted after a sync job reaches a terminal success state."""

    repository_id: str = ""
    sync_job_id: str = ""
    job_type: str = ""
    last_commit_sha: str | None = None


@dataclass(frozen=True, slots=True)
class WebhookProcessed(DomainEvent):
    webhook_event_id: str = ""
    event_type: str = ""
    action: str | None = None
    repository_id: str | None = None
    installation_id: str | None = None


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_cls: type[DomainEvent], handler: Handler) -> None:
        self._handlers[event_cls.__name__].append(handler)
        logger.info(
            "Event handler registered",
            extra={"event": event_cls.__name__, "handler": getattr(handler, "__name__", str(handler))},
        )

    def on(self, event_cls: type[DomainEvent]) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            self.subscribe(event_cls, handler)
            return handler

        return decorator

    async def publish(self, event: DomainEvent) -> None:
        name = event.event_type
        handlers = list(self._handlers.get(name, []))
        logger.info(
            "Domain event published",
            extra={"event": name, "event_id": event.event_id, "handlers": len(handlers)},
        )
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result) or isinstance(result, Awaitable):
                    await result  # type: ignore[arg-type]
            except Exception:
                logger.exception(
                    "Domain event handler failed",
                    extra={"event": name, "handler": getattr(handler, "__name__", str(handler))},
                )


event_bus = EventBus()
