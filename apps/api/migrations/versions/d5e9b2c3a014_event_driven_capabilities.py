"""Event-driven prep: checkpoints, rate limits, repository capabilities."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d5e9b2c3a014"
down_revision: Union[str, None] = "c4f8a1b2d903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "repositories",
        sa.Column("supports_ai", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "repositories",
        sa.Column("supports_indexing", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "repositories",
        sa.Column("supports_pr_review", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "repositories",
        sa.Column("supports_chat", sa.Boolean(), server_default="false", nullable=False),
    )

    op.create_table(
        "repository_sync_checkpoints",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("last_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("last_webhook_delivery", sa.String(length=100), nullable=True),
        sa.Column("last_sync_cursor", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", name="uq_sync_checkpoints_repository_id"),
    )
    op.create_index(
        "ix_sync_checkpoints_repository_id",
        "repository_sync_checkpoints",
        ["repository_id"],
    )

    op.create_table(
        "github_rate_limits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("installation_id", sa.String(length=64), nullable=False),
        sa.Column("resource", sa.String(length=50), nullable=False),
        sa.Column("remaining", sa.Integer(), nullable=False),
        sa.Column("limit", sa.Integer(), nullable=False),
        sa.Column("reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "installation_id", "resource", name="uq_github_rate_limits_install_resource"
        ),
    )
    op.create_index(
        "ix_github_rate_limits_installation_id",
        "github_rate_limits",
        ["installation_id"],
    )


def downgrade() -> None:
    op.drop_table("github_rate_limits")
    op.drop_table("repository_sync_checkpoints")
    op.drop_column("repositories", "supports_chat")
    op.drop_column("repositories", "supports_pr_review")
    op.drop_column("repositories", "supports_indexing")
    op.drop_column("repositories", "supports_ai")
