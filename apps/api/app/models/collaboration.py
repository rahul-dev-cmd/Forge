"""SQLAlchemy 2.0 ORM Models for Collaboration, Quotas, and Feature Flags."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    String,
    ForeignKey,
    UUID,
    Integer,
    DateTime,
    Text,
    Boolean,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDMixin, TimestampMixin


class WorkspaceActivity(Base, UUIDMixin, TimestampMixin):
    """Activity feed audit log for workspace operations."""

    __tablename__ = "workspace_activities"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )


class RepositoryComment(Base, UUIDMixin, TimestampMixin):
    """Inline code comments and discussion threads."""

    __tablename__ = "repository_comments"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    mentions: Mapped[list[str] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )


class NotificationRecord(Base, UUIDMixin, TimestampMixin):
    """User and team notifications with read status."""

    __tablename__ = "notification_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), default="info", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WorkspaceQuota(Base, UUIDMixin, TimestampMixin):
    """Workspace usage plan limits and billing foundation."""

    __tablename__ = "workspace_quotas"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    plan_name: Mapped[str] = mapped_column(String(50), default="pro", nullable=False)
    max_tokens_monthly: Mapped[int] = mapped_column(Integer, default=1_000_000, nullable=False)
    max_repositories: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    max_vectors: Mapped[int] = mapped_column(Integer, default=100_000, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=10_000, nullable=False)


class FeatureFlagRecord(Base, UUIDMixin, TimestampMixin):
    """System feature flags with workspace overrides."""

    __tablename__ = "feature_flag_records"

    flag_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_enabled_globally: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled_workspace_ids: Mapped[list[str] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )
