import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, ForeignKey, UUID, Integer, BigInteger, DateTime, Text,
    UniqueConstraint, Index, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import PullRequestStatus, IssueStatus


class Branch(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("repository_id", "name", name="uq_branches_repo_name"),
        Index("ix_branches_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latest_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="branches")


class Commit(Base, UUIDMixin, TimestampMixin):
    """Commit metadata only — no source code or diffs."""

    __tablename__ = "commits"
    __table_args__ = (
        UniqueConstraint("repository_id", "commit_sha", name="uq_commits_repo_sha"),
        Index("ix_commits_repository_id", "repository_id"),
        Index("ix_commits_committed_at", "committed_at"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True
    )
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    commit_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    additions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deletions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_files: Mapped[int | None] = mapped_column(Integer, nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    committed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="commits")


class PullRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repository_id", "provider_pr_id", name="uq_prs_repo_provider_id"),
        Index("ix_pull_requests_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    provider_pr_id: Mapped[str] = mapped_column(String(64), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=PullRequestStatus.OPEN.value, nullable=False
    )
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    draft: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="pull_requests")


class Issue(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("repository_id", "provider_issue_id", name="uq_issues_repo_provider_id"),
        Index("ix_issues_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    provider_issue_id: Mapped[str] = mapped_column(String(64), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=IssueStatus.OPEN.value, nullable=False
    )
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    labels: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="issues")


class Contributor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contributors"
    __table_args__ = (
        UniqueConstraint("repository_id", "provider_user_id", name="uq_contributors_repo_user"),
        Index("ix_contributors_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    provider_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    login: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    contributions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="contributors")


class RepositoryLanguage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "repository_languages"
    __table_args__ = (
        UniqueConstraint("repository_id", "language", name="uq_repo_languages_repo_lang"),
        Index("ix_repository_languages_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(100), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="languages")


class RepositoryTopic(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "repository_topics"
    __table_args__ = (
        UniqueConstraint("repository_id", "topic", name="uq_repo_topics_repo_topic"),
        Index("ix_repository_topics_repository_id", "repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(100), nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="topics")
