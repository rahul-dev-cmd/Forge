import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, UUID, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import JobStatus, SyncJobType


class RepositorySync(Base, UUIDMixin, TimestampMixin):
    """
    Tracks repository synchronization / import jobs.
    """

    __tablename__ = "repository_syncs"
    __table_args__ = (
        Index("ix_repository_syncs_repository_id", "repository_id"),
        Index("ix_repository_syncs_status", "status"),
        Index("ix_repository_syncs_job_type", "job_type"),
    )

    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=True
    )
    installation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_type: Mapped[str] = mapped_column(
        String(50), default=SyncJobType.REPOSITORY_SYNC.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=JobStatus.QUEUED.value, nullable=False
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    branches_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    commits_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pull_requests_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    issues_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contributors_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    arq_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    repository: Mapped["Repository | None"] = relationship(
        "Repository", back_populates="sync_jobs"
    )
