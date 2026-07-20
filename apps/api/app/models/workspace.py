import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import WorkspaceRole

class Workspace(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workspaces"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="workspaces")
    memberships: Mapped[list["WorkspaceMember"]] = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    repositories: Mapped[list["Repository"]] = relationship("Repository", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base, UUIDMixin):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=WorkspaceRole.DEVELOPER.value, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    invited_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="workspace_memberships", foreign_keys=[user_id])
