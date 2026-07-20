"""Sync checkpoints and GitHub rate-limit persistence."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, UUID, Integer, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDMixin, TimestampMixin


class RepositorySyncCheckpoint(Base, UUIDMixin, TimestampMixin):
    """
    Per-repository sync cursors for incremental synchronization.
    """

    __tablename__ = "repository_sync_checkpoints"
    __table_args__ = (
        UniqueConstraint("repository_id", name="uq_sync_checkpoints_repository_id"),
        Index("ix_sync_checkpoints_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    last_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_webhook_delivery: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_sync_cursor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="sync_checkpoint"
    )


class GitHubRateLimit(Base, UUIDMixin, TimestampMixin):
    """
    Persisted GitHub API rate-limit snapshot per installation (and optional resource).
    """

    __tablename__ = "github_rate_limits"
    __table_args__ = (
        UniqueConstraint(
            "installation_id", "resource", name="uq_github_rate_limits_install_resource"
        ),
        Index("ix_github_rate_limits_installation_id", "installation_id"),
    )

    installation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(50), default="core", nullable=False)
    remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    limit: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)
    reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
