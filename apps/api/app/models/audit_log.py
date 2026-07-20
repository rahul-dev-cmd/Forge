import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, UUID, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin

class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. login, project_creation, settings_change
    target_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. project, workspace, user, settings
    target_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    actor: Mapped["User"] = relationship("User", back_populates="audit_logs")
