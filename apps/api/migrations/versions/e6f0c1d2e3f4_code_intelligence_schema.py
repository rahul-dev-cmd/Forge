"""Milestone 7 — Code Intelligence & Indexing Schema."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e6f0c1d2e3f4"
down_revision: Union[str, None] = "d5e9b2c3a014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. repository_snapshots
    op.create_table(
        "repository_snapshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("commit_sha", sa.String(length=64), nullable=False),
        sa.Column("branch", sa.String(length=255), server_default="main", nullable=False),
        sa.Column("repository_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("snapshot_metadata", postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. repository_indexes
    op.create_table(
        "repository_indexes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=True),
        sa.Column("commit_sha", sa.String(length=64), nullable=False),
        sa.Column("branch", sa.String(length=255), server_default="main", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="pending", nullable=False),
        sa.Column("ast_version", sa.String(length=50), server_default="v1.0", nullable=False),
        sa.Column("total_files", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_symbols", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_chunks", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_lines", sa.Integer(), server_default="0", nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["repository_snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. indexed_files
    op.create_table(
        "indexed_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("index_id", sa.UUID(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=50), server_default="unknown", nullable=False),
        sa.Column("size_bytes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("line_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("symbol_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("chunk_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cyclomatic_complexity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("ast_version", sa.String(length=50), server_default="v1.0", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="completed", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["index_id"], ["repository_indexes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 4. code_symbols
    op.create_table(
        "code_symbols",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("indexed_file_id", sa.UUID(), nullable=False),
        sa.Column("parent_symbol_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("fqn", sa.String(length=512), nullable=False),
        sa.Column("namespace", sa.String(length=255), nullable=True),
        sa.Column("package", sa.String(length=255), nullable=True),
        sa.Column("symbol_type", sa.String(length=50), nullable=False),
        sa.Column("visibility", sa.String(length=30), server_default="public", nullable=False),
        sa.Column("modifiers", postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"), nullable=True),
        sa.Column("return_type", sa.String(length=255), nullable=True),
        sa.Column("parameter_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("docstring", sa.Text(), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("start_column", sa.Integer(), server_default="0", nullable=False),
        sa.Column("end_column", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indexed_file_id"], ["indexed_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_symbol_id"], ["code_symbols.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 5. code_references
    op.create_table(
        "code_references",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("symbol_id", sa.UUID(), nullable=True),
        sa.Column("source_file_id", sa.UUID(), nullable=False),
        sa.Column("target_file_id", sa.UUID(), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_file_id"], ["indexed_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol_id"], ["code_symbols.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_file_id"], ["indexed_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 6. code_chunks
    op.create_table(
        "code_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("indexed_file_id", sa.UUID(), nullable=False),
        sa.Column("parent_symbol_id", sa.UUID(), nullable=True),
        sa.Column("branch", sa.String(length=255), server_default="main", nullable=False),
        sa.Column("chunk_hash", sa.String(length=64), nullable=False),
        sa.Column("chunk_type", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indexed_file_id"], ["indexed_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_symbol_id"], ["code_symbols.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 7. import_graphs
    op.create_table(
        "import_graphs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("source_file_path", sa.String(length=1024), nullable=False),
        sa.Column("target_module", sa.String(length=512), nullable=False),
        sa.Column("imported_symbols", postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 8. call_graphs
    op.create_table(
        "call_graphs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("caller_fqn", sa.String(length=512), nullable=False),
        sa.Column("callee_fqn", sa.String(length=512), nullable=False),
        sa.Column("caller_file_path", sa.String(length=1024), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 9. dependency_graphs
    op.create_table(
        "dependency_graphs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("source_path", sa.String(length=1024), nullable=False),
        sa.Column("target_path", sa.String(length=1024), nullable=False),
        sa.Column("dependency_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 10. repository_metrics
    op.create_table(
        "repository_metrics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("total_files", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_lines", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_symbols", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_chunks", sa.Integer(), server_default="0", nullable=False),
        sa.Column("average_complexity", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("maintainability_index", sa.Float(), server_default="100.0", nullable=False),
        sa.Column("largest_file_path", sa.String(length=1024), nullable=True),
        sa.Column("largest_file_bytes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deepest_directory_depth", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_classes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_functions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_methods", sa.Integer(), server_default="0", nullable=False),
        sa.Column("todo_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("fixme_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("documentation_coverage_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("average_function_length", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("language_distribution", postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", name="uq_repository_metrics_repository_id"),
    )

    # 11. index_jobs
    op.create_table(
        "index_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="queued", nullable=False),
        sa.Column("progress_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("processed_files", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_files", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 12. index_checkpoints
    op.create_table(
        "index_checkpoints",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("last_processed_file", sa.String(length=1024), nullable=True),
        sa.Column("processed_files_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("checkpoint_data", postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["index_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 13. language_statistics
    op.create_table(
        "language_statistics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("file_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("line_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("bytes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("percentage", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("language_statistics")
    op.drop_table("index_checkpoints")
    op.drop_table("index_jobs")
    op.drop_table("repository_metrics")
    op.drop_table("dependency_graphs")
    op.drop_table("call_graphs")
    op.drop_table("import_graphs")
    op.drop_table("code_chunks")
    op.drop_table("code_references")
    op.drop_table("code_symbols")
    op.drop_table("indexed_files")
    op.drop_table("repository_indexes")
    op.drop_table("repository_snapshots")
