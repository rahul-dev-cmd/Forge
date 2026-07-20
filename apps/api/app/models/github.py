import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, UUID, BigInteger, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import InstallationStatus


class GitHubInstallation(Base, UUIDMixin, TimestampMixin):
    """
    GitHub App installation belonging to a user/workspace.
    Supports multiple installations (orgs/accounts) per user.
    """

    __tablename__ = "github_installations"
    __table_args__ = (
        UniqueConstraint("installation_id", name="uq_github_installations_installation_id"),
        Index("ix_github_installations_user_id", "user_id"),
        Index("ix_github_installations_workspace_id", "workspace_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    installation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), default="Organization", nullable=False)
    account_avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    permissions: Mapped[str | None] = mapped_column(Text, nullable=True)
    events: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=InstallationStatus.ACTIVE.value, nullable=False
    )
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Encrypted OAuth user access token (account linking) — never expose in API responses
    encrypted_user_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repositories: Mapped[list["Repository"]] = relationship(
        "Repository", back_populates="github_installation"
    )


class GitHubAccountLink(Base, UUIDMixin, TimestampMixin):
    """
    Links a Forge user to their GitHub OAuth identity (separate from App installations).
    """

    __tablename__ = "github_account_links"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_github_account_links_user_id"),
        UniqueConstraint("github_user_id", name="uq_github_account_links_github_user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    github_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    github_login: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
