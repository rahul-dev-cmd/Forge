import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, UUID, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin

class RepositoryActivity(Base, UUIDMixin):
    __tablename__ = "repository_activities"

    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. Import, Sync, Commit Indexed
    activity_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="activities")
    actor: Mapped["User"] = relationship("User")
