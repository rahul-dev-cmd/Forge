import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, UUID, Integer, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import RepositoryProvider, RepositoryVisibility, SyncStatus, ConnectionStatus


class Repository(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "repositories"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    github_installation_fk: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("github_installations.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(
        String(50), default=RepositoryProvider.GITHUB.value, nullable=False
    )
    # Provider repository ID (GitHub numeric id as string)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    provider_repository_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    installation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    clone_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    html_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    visibility: Mapped[str] = mapped_column(
        String(50), default=RepositoryVisibility.PRIVATE.value, nullable=False
    )
    connection_status: Mapped[str] = mapped_column(
        String(50), default=ConnectionStatus.CONNECTED.value, nullable=False
    )

    # Sync state
    sync_status: Mapped[str] = mapped_column(
        String(50), default=SyncStatus.IDLE.value, nullable=False
    )
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_webhook_delivery_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Repository statistics (metadata only)
    stars_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watchers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    size_kb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    primary_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    readme_exists: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    readme_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_fork: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Ready for future AI indexing (Milestone 7+) — not used yet
    indexing_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Capability flags — gate future features without schema rewrites
    supports_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    supports_indexing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    supports_pr_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_chat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="repositories")
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="repositories")
    github_installation: Mapped["GitHubInstallation | None"] = relationship(
        "GitHubInstallation", back_populates="repositories"
    )
    settings: Mapped["RepositorySettings"] = relationship(
        "RepositorySettings",
        back_populates="repository",
        cascade="all, delete-orphan",
        uselist=False,
    )
    sync_checkpoint: Mapped["RepositorySyncCheckpoint | None"] = relationship(
        "RepositorySyncCheckpoint",
        back_populates="repository",
        cascade="all, delete-orphan",
        uselist=False,
    )
    activities: Mapped[list["RepositoryActivity"]] = relationship(
        "RepositoryActivity", back_populates="repository", cascade="all, delete-orphan"
    )
    branches: Mapped[list["Branch"]] = relationship(
        "Branch", back_populates="repository", cascade="all, delete-orphan"
    )
    commits: Mapped[list["Commit"]] = relationship(
        "Commit", back_populates="repository", cascade="all, delete-orphan"
    )
    pull_requests: Mapped[list["PullRequest"]] = relationship(
        "PullRequest", back_populates="repository", cascade="all, delete-orphan"
    )
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="repository", cascade="all, delete-orphan"
    )
    contributors: Mapped[list["Contributor"]] = relationship(
        "Contributor", back_populates="repository", cascade="all, delete-orphan"
    )
    languages: Mapped[list["RepositoryLanguage"]] = relationship(
        "RepositoryLanguage", back_populates="repository", cascade="all, delete-orphan"
    )
    topics: Mapped[list["RepositoryTopic"]] = relationship(
        "RepositoryTopic", back_populates="repository", cascade="all, delete-orphan"
    )
    sync_jobs: Mapped[list["RepositorySync"]] = relationship(
        "RepositorySync", back_populates="repository", cascade="all, delete-orphan"
    )
    webhook_events: Mapped[list["WebhookEvent"]] = relationship(
        "WebhookEvent", back_populates="repository"
    )


class RepositorySettings(Base, UUIDMixin):
    __tablename__ = "repository_settings"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    indexing_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_interval: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="settings")
