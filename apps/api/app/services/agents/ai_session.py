"""AI Session Object — Stateful context wrapper for multi-agent executions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class AISession:
    """Stateful AI session wrapping conversation, repository, workspace, and context."""

    conversation_id: uuid.UUID
    workspace_id: uuid.UUID
    repository_id: uuid.UUID | None
    user_id: uuid.UUID
    db: AsyncSession
    active_agent: str = "coordinator"
    permissions: list[str] = field(default_factory=lambda: ["repository.read", "code.search"])
    context_package: dict[str, Any] | None = None
    tool_state: dict[str, Any] = field(default_factory=dict)
