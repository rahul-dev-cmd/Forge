import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, UUID, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import ProjectStatus, ProjectPriority

class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    # Core extended project configurations
    status: Mapped[str] = mapped_column(String(50), default=ProjectStatus.ACTIVE.value, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default=ProjectPriority.MEDIUM.value, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB().with_variant(JSON, "sqlite"), default=list, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    visibility: Mapped[str] = mapped_column(String(50), default="private", nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Optimistic locking version
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="projects")
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    settings: Mapped["ProjectSettings"] = relationship("ProjectSettings", back_populates="project", cascade="all, delete-orphan", uselist=False)
    repositories: Mapped[list["Repository"]] = relationship("Repository", back_populates="project", cascade="all, delete-orphan")

class ProjectSettings(Base, UUIDMixin):
    __tablename__ = "project_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    coding_style: Mapped[str] = mapped_column(String(100), default="standard", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(100), default="python", nullable=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="settings")
