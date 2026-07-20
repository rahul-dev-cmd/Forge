"""SQLAlchemy 2.0 ORM Models for Milestone 7 — Code Intelligence & Indexing."""

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
    IndexStatus,
    IndexJobType,
    SymbolType,
    ReferenceType,
    DependencyType,
    ChunkType,
)


class RepositorySnapshot(Base, UUIDMixin, TimestampMixin):
    """
    Point-in-time snapshot of a repository commit/branch for deterministic indexing.
    """

    __tablename__ = "repository_snapshots"
    __table_args__ = (
        Index("ix_repo_snapshots_repo_commit", "repository_id", "commit_sha"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    repository_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    snapshot_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )

    repository: Mapped["Repository"] = relationship("Repository")
    indexes: Mapped[list["RepositoryIndex"]] = relationship(
        "RepositoryIndex", back_populates="snapshot", cascade="all, delete-orphan"
    )


class RepositoryIndex(Base, UUIDMixin, TimestampMixin):
    """
    Overall index state for a repository snapshot.
    """

    __tablename__ = "repository_indexes"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repository_snapshots.id", ondelete="SET NULL"), nullable=True
    )
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=IndexStatus.PENDING.value, nullable=False)
    ast_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)

    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_symbols: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    snapshot: Mapped["RepositorySnapshot | None"] = relationship(
        "RepositorySnapshot", back_populates="indexes"
    )
    indexed_files: Mapped[list["IndexedFile"]] = relationship(
        "IndexedFile", back_populates="index", cascade="all, delete-orphan"
    )


class IndexedFile(Base, UUIDMixin, TimestampMixin):
    """
    Single indexed file entry within a repository index.
    """

    __tablename__ = "indexed_files"
    __table_args__ = (
        UniqueConstraint("index_id", "file_path", name="uq_indexed_files_index_path"),
        Index("ix_indexed_files_repo_path", "repository_id", "file_path"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    index_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repository_indexes.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False) # Clean relative path
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    symbol_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ast_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=IndexStatus.COMPLETED.value, nullable=False)

    index: Mapped["RepositoryIndex"] = relationship(
        "RepositoryIndex", back_populates="indexed_files"
    )
    symbols: Mapped[list["CodeSymbol"]] = relationship(
        "CodeSymbol", back_populates="indexed_file", cascade="all, delete-orphan"
    )
    chunks: Mapped[list["CodeChunk"]] = relationship(
        "CodeChunk", back_populates="indexed_file", cascade="all, delete-orphan"
    )


class CodeSymbol(Base, UUIDMixin, TimestampMixin):
    """
    Extracted code symbol (Class, Function, Method, Interface, Enum, Variable, Constant).
    """

    __tablename__ = "code_symbols"
    __table_args__ = (
        Index("ix_code_symbols_repo_name", "repository_id", "name"),
        Index("ix_code_symbols_fqn", "repository_id", "fqn"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    indexed_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indexed_files.id", ondelete="CASCADE"), nullable=False
    )
    parent_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_symbols.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fqn: Mapped[str] = mapped_column(String(512), nullable=False) # Fully Qualified Name
    namespace: Mapped[str | None] = mapped_column(String(255), nullable=True)
    package: Mapped[str | None] = mapped_column(String(255), nullable=True)

    symbol_type: Mapped[str] = mapped_column(String(50), default=SymbolType.FUNCTION.value, nullable=False)
    visibility: Mapped[str] = mapped_column(String(30), default="public", nullable=False) # public/private/protected
    modifiers: Mapped[list[str] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )

    return_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parameter_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    docstring: Mapped[str | None] = mapped_column(Text, nullable=True)

    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    start_column: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    end_column: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    indexed_file: Mapped["IndexedFile"] = relationship("IndexedFile", back_populates="symbols")
    parent_symbol: Mapped["CodeSymbol | None"] = relationship("CodeSymbol", remote_side="CodeSymbol.id")


class CodeReference(Base, UUIDMixin, TimestampMixin):
    """
    Symbol reference mapping across codebase locations.
    """

    __tablename__ = "code_references"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_symbols.id", ondelete="SET NULL"), nullable=True
    )
    source_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indexed_files.id", ondelete="CASCADE"), nullable=False
    )
    target_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indexed_files.id", ondelete="CASCADE"), nullable=True
    )

    reference_type: Mapped[str] = mapped_column(String(50), default=ReferenceType.CALL.value, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)


class CodeChunk(Base, UUIDMixin, TimestampMixin):
    """
    Pre-embedding code chunk boundary representation.
    No raw content stored to preserve Git as single source of truth.
    """

    __tablename__ = "code_chunks"
    __table_args__ = (
        Index("ix_code_chunks_repo_file", "repository_id", "indexed_file_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    indexed_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indexed_files.id", ondelete="CASCADE"), nullable=False
    )
    parent_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_symbols.id", ondelete="SET NULL"), nullable=True
    )

    branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    chunk_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(50), default=ChunkType.FUNCTION.value, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)

    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    indexed_file: Mapped["IndexedFile"] = relationship("IndexedFile", back_populates="chunks")


class ImportGraph(Base, UUIDMixin, TimestampMixin):
    """
    Module import and export relationship model.
    """

    __tablename__ = "import_graphs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_module: Mapped[str] = mapped_column(String(512), nullable=False)
    imported_symbols: Mapped[list[str] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )


class CallGraph(Base, UUIDMixin, TimestampMixin):
    """
    Caller -> Callee symbol relationship graph model.
    """

    __tablename__ = "call_graphs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    caller_fqn: Mapped[str] = mapped_column(String(512), nullable=False)
    callee_fqn: Mapped[str] = mapped_column(String(512), nullable=False)
    caller_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)


class DependencyGraph(Base, UUIDMixin, TimestampMixin):
    """
    File-to-file and Package-to-package dependency relationships.
    """

    __tablename__ = "dependency_graphs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(50), default=DependencyType.IMPORT.value, nullable=False)


class RepositoryMetric(Base, UUIDMixin, TimestampMixin):
    """
    Comprehensive aggregated codebase analytics and metrics.
    """

    __tablename__ = "repository_metrics"
    __table_args__ = (
        UniqueConstraint("repository_id", name="uq_repository_metrics_repository_id"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_symbols: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    average_complexity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    maintainability_index: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    largest_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    largest_file_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deepest_directory_depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    total_classes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_functions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_methods: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    todo_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fixme_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    documentation_coverage_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_function_length: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    language_distribution: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )


class IndexJob(Base, UUIDMixin, TimestampMixin):
    """
    Background worker job execution record for indexing pipelines.
    """

    __tablename__ = "index_jobs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[str] = mapped_column(String(50), default=IndexJobType.REPOSITORY_INDEX.value, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=IndexStatus.QUEUED.value, nullable=False)

    progress_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    processed_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IndexCheckpoint(Base, UUIDMixin, TimestampMixin):
    """
    Resumable cursor checkpoint for background worker resumption.
    """

    __tablename__ = "index_checkpoints"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("index_jobs.id", ondelete="CASCADE"), nullable=False
    )

    last_processed_file: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    processed_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checkpoint_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )


class LanguageStatistic(Base, UUIDMixin, TimestampMixin):
    """
    Language statistics per repository.
    """

    __tablename__ = "language_statistics"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
