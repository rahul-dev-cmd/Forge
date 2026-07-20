"""SQLAlchemy 2.0 ORM Models for Milestone 8 — AI Knowledge Layer."""

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
    Float,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import (
    EmbeddingStatus,
    EmbeddingJobType,
    EmbeddingProviderType,
    SearchType,
)


class EmbeddingJob(Base, UUIDMixin, TimestampMixin):
    """
    Background worker job execution record for embedding pipelines.
    """

    __tablename__ = "embedding_jobs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[str] = mapped_column(
        String(50), default=EmbeddingJobType.REPOSITORY_EMBED.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=EmbeddingStatus.QUEUED.value, nullable=False
    )

    progress_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    processed_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EmbeddingVersion(Base, UUIDMixin, TimestampMixin):
    """
    Tracks active vector index collection version for a repository snapshot.
    """

    __tablename__ = "embedding_versions"
    __table_args__ = (
        Index("ix_embedding_versions_repo_snap", "repository_id", "snapshot_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repository_snapshots.id", ondelete="CASCADE"), nullable=False
    )

    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    version_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EmbeddingRecord(Base, UUIDMixin, TimestampMixin):
    """
    Mapping record linking a CodeChunk to a Qdrant vector point ID.
    """

    __tablename__ = "embedding_records"
    __table_args__ = (
        Index("ix_embedding_records_chunk", "chunk_id"),
        Index("ix_embedding_records_repo_vector", "repository_id", "vector_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repository_snapshots.id", ondelete="CASCADE"), nullable=False
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_chunks.id", ondelete="CASCADE"), nullable=False
    )

    vector_id: Mapped[str] = mapped_column(String(128), nullable=False)
    context_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA256(repo_id:branch:file:lines:content)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class RetrievalSession(Base, UUIDMixin, TimestampMixin):
    """
    Logs context retrieval operations.
    """

    __tablename__ = "retrieval_sessions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    search_type: Mapped[str] = mapped_column(String(30), default=SearchType.HYBRID.value, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class SearchHistory(Base, UUIDMixin, TimestampMixin):
    """
    Stores past semantic & hybrid search queries and analytics.
    """

    __tablename__ = "search_histories"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("retrieval_sessions.id", ondelete="CASCADE"), nullable=True
    )

    query: Mapped[str] = mapped_column(Text, nullable=False)
    search_type: Mapped[str] = mapped_column(String(30), default=SearchType.HYBRID.value, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    top_similarity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    top_bm25_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class KnowledgeContext(Base, UUIDMixin, TimestampMixin):
    """
    Stores standardized ContextPackage snapshots for auditability.
    """

    __tablename__ = "knowledge_contexts"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("retrieval_sessions.id", ondelete="CASCADE"), nullable=False
    )

    query: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    package_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=False
    )


class RepositoryKnowledge(Base, UUIDMixin, TimestampMixin):
    """
    Aggregated AI Knowledge metrics per repository.
    """

    __tablename__ = "repository_knowledges"
    __table_args__ = (
        UniqueConstraint("repository_id", name="uq_repository_knowledges_repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )

    total_vectors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="all-MiniLM-L6-v2", nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, default=384, nullable=False)
    embedding_health: Mapped[str] = mapped_column(String(50), default="ready", nullable=False)
