import uuid
from sqlalchemy import String, Boolean, ForeignKey, UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import RepositoryProvider, RepositoryVisibility

class Repository(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "repositories"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default=RepositoryProvider.GITHUB.value, nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    clone_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    installation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Core extended repository attributes
    visibility: Mapped[str] = mapped_column(String(50), default=RepositoryVisibility.PRIVATE.value, nullable=False)
    connection_status: Mapped[str] = mapped_column(String(50), default="connected", nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="repositories")
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="repositories")
    settings: Mapped["RepositorySettings"] = relationship("RepositorySettings", back_populates="repository", cascade="all, delete-orphan", uselist=False)
    activities: Mapped[list["RepositoryActivity"]] = relationship("RepositoryActivity", back_populates="repository", cascade="all, delete-orphan")

class RepositorySettings(Base, UUIDMixin):
    __tablename__ = "repository_settings"

    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), unique=True, nullable=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    indexing_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_interval: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="settings")
