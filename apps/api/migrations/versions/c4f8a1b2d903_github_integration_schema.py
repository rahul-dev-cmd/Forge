"""GitHub integration & repository intelligence schema (Milestone 6)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c4f8a1b2d903"
down_revision: Union[str, None] = "8c8e7e2b9b52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "github_installations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=True),
        sa.Column("installation_id", sa.String(length=64), nullable=False),
        sa.Column("account_login", sa.String(length=255), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("account_type", sa.String(length=50), nullable=False),
        sa.Column("account_avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("permissions", sa.Text(), nullable=True),
        sa.Column("events", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("encrypted_user_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("installation_id", name="uq_github_installations_installation_id"),
    )
    op.create_index("ix_github_installations_user_id", "github_installations", ["user_id"])
    op.create_index("ix_github_installations_workspace_id", "github_installations", ["workspace_id"])

    op.create_table(
        "github_account_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("github_user_id", sa.String(length=64), nullable=False),
        sa.Column("github_login", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("encrypted_access_token", sa.Text(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_github_account_links_user_id"),
        sa.UniqueConstraint("github_user_id", name="uq_github_account_links_github_user_id"),
    )

    # Extend repositories
    op.add_column("repositories", sa.Column("github_installation_fk", sa.UUID(), nullable=True))
    op.add_column("repositories", sa.Column("provider_repository_id", sa.String(length=64), nullable=True))
    op.add_column("repositories", sa.Column("owner", sa.String(length=255), nullable=True))
    op.add_column("repositories", sa.Column("full_name", sa.String(length=512), nullable=True))
    op.add_column("repositories", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("repositories", sa.Column("html_url", sa.String(length=1000), nullable=True))
    op.add_column("repositories", sa.Column("sync_status", sa.String(length=50), server_default="idle", nullable=False))
    op.add_column("repositories", sa.Column("sync_error", sa.Text(), nullable=True))
    op.add_column("repositories", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("repositories", sa.Column("last_webhook_delivery_id", sa.String(length=100), nullable=True))
    op.add_column("repositories", sa.Column("stars_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("repositories", sa.Column("forks_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("repositories", sa.Column("watchers_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("repositories", sa.Column("open_issues_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("repositories", sa.Column("size_kb", sa.Integer(), server_default="0", nullable=False))
    op.add_column("repositories", sa.Column("license", sa.String(length=100), nullable=True))
    op.add_column("repositories", sa.Column("primary_language", sa.String(length=100), nullable=True))
    op.add_column("repositories", sa.Column("readme_exists", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("repositories", sa.Column("readme_path", sa.String(length=255), nullable=True))
    op.add_column("repositories", sa.Column("is_archived", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("repositories", sa.Column("is_fork", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("repositories", sa.Column("indexing_ready", sa.Boolean(), server_default="false", nullable=False))
    op.create_foreign_key(
        "fk_repositories_github_installation",
        "repositories",
        "github_installations",
        ["github_installation_fk"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_repositories_provider_repository_id", "repositories", ["provider_repository_id"])

    op.create_table(
        "repository_syncs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=True),
        sa.Column("installation_id", sa.String(length=64), nullable=True),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("branches_synced", sa.Integer(), nullable=False),
        sa.Column("commits_synced", sa.Integer(), nullable=False),
        sa.Column("pull_requests_synced", sa.Integer(), nullable=False),
        sa.Column("issues_synced", sa.Integer(), nullable=False),
        sa.Column("contributors_synced", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.String(length=100), nullable=True),
        sa.Column("arq_job_id", sa.String(length=100), nullable=True),
        sa.Column("triggered_by", sa.UUID(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repository_syncs_repository_id", "repository_syncs", ["repository_id"])
    op.create_index("ix_repository_syncs_status", "repository_syncs", ["status"])
    op.create_index("ix_repository_syncs_job_type", "repository_syncs", ["job_type"])

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("webhook_delivery_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=True),
        sa.Column("installation_id", sa.String(length=64), nullable=True),
        sa.Column("provider_repository_id", sa.String(length=64), nullable=True),
        sa.Column("repository_id", sa.UUID(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("arq_job_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("webhook_delivery_id"),
    )
    op.create_index("ix_webhook_events_delivery_id", "webhook_events", ["webhook_delivery_id"])
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])
    op.create_index("ix_webhook_events_status", "webhook_events", ["status"])
    op.create_index("ix_webhook_events_installation_id", "webhook_events", ["installation_id"])

    op.create_table(
        "branches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("latest_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "name", name="uq_branches_repo_name"),
    )
    op.create_index("ix_branches_repository_id", "branches", ["repository_id"])

    op.create_table(
        "commits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=True),
        sa.Column("commit_sha", sa.String(length=64), nullable=False),
        sa.Column("parent_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("author_name", sa.String(length=255), nullable=True),
        sa.Column("author_email", sa.String(length=255), nullable=True),
        sa.Column("author_login", sa.String(length=255), nullable=True),
        sa.Column("commit_message", sa.Text(), nullable=True),
        sa.Column("additions", sa.Integer(), nullable=True),
        sa.Column("deletions", sa.Integer(), nullable=True),
        sa.Column("changed_files", sa.Integer(), nullable=True),
        sa.Column("html_url", sa.String(length=1000), nullable=True),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "commit_sha", name="uq_commits_repo_sha"),
    )
    op.create_index("ix_commits_repository_id", "commits", ["repository_id"])
    op.create_index("ix_commits_committed_at", "commits", ["committed_at"])

    op.create_table(
        "pull_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("provider_pr_id", sa.String(length=64), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_branch", sa.String(length=255), nullable=True),
        sa.Column("target_branch", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("author_login", sa.String(length=255), nullable=True),
        sa.Column("author_avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("html_url", sa.String(length=1000), nullable=True),
        sa.Column("draft", sa.Boolean(), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "provider_pr_id", name="uq_prs_repo_provider_id"),
    )
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"])

    op.create_table(
        "issues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("provider_issue_id", sa.String(length=64), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("author_login", sa.String(length=255), nullable=True),
        sa.Column("author_avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("html_url", sa.String(length=1000), nullable=True),
        sa.Column("labels", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "provider_issue_id", name="uq_issues_repo_provider_id"),
    )
    op.create_index("ix_issues_repository_id", "issues", ["repository_id"])

    op.create_table(
        "contributors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("provider_user_id", sa.String(length=64), nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("html_url", sa.String(length=1000), nullable=True),
        sa.Column("contributions", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "provider_user_id", name="uq_contributors_repo_user"),
    )
    op.create_index("ix_contributors_repository_id", "contributors", ["repository_id"])

    op.create_table(
        "repository_languages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("language", sa.String(length=100), nullable=False),
        sa.Column("bytes", sa.BigInteger(), nullable=False),
        sa.Column("percentage", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "language", name="uq_repo_languages_repo_lang"),
    )
    op.create_index("ix_repository_languages_repository_id", "repository_languages", ["repository_id"])

    op.create_table(
        "repository_topics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "topic", name="uq_repo_topics_repo_topic"),
    )
    op.create_index("ix_repository_topics_repository_id", "repository_topics", ["repository_id"])


def downgrade() -> None:
    op.drop_table("repository_topics")
    op.drop_table("repository_languages")
    op.drop_table("contributors")
    op.drop_table("issues")
    op.drop_table("pull_requests")
    op.drop_table("commits")
    op.drop_table("branches")
    op.drop_table("webhook_events")
    op.drop_table("repository_syncs")
    op.drop_constraint("fk_repositories_github_installation", "repositories", type_="foreignkey")
    op.drop_index("ix_repositories_provider_repository_id", table_name="repositories")
    for col in [
        "github_installation_fk",
        "provider_repository_id",
        "owner",
        "full_name",
        "description",
        "html_url",
        "sync_status",
        "sync_error",
        "last_synced_at",
        "last_webhook_delivery_id",
        "stars_count",
        "forks_count",
        "watchers_count",
        "open_issues_count",
        "size_kb",
        "license",
        "primary_language",
        "readme_exists",
        "readme_path",
        "is_archived",
        "is_fork",
        "indexing_ready",
    ]:
        op.drop_column("repositories", col)
    op.drop_table("github_account_links")
    op.drop_table("github_installations")
