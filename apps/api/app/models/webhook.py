import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, UUID, Integer, DateTime, Text, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import WebhookProcessingStatus


class WebhookEvent(Base, UUIDMixin, TimestampMixin):
    """
    Stores GitHub webhook deliveries for audit, retry, and observability.
    """

    __tablename__ = "webhook_events"
    __table_args__ = (
        Index("ix_webhook_events_delivery_id", "webhook_delivery_id"),
        Index("ix_webhook_events_event_type", "event_type"),
        Index("ix_webhook_events_status", "status"),
        Index("ix_webhook_events_installation_id", "installation_id"),
    )

    webhook_delivery_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    installation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_repository_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="SET NULL"), nullable=True
    )
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default=WebhookProcessingStatus.RECEIVED.value, nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    arq_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    repository: Mapped["Repository | None"] = relationship(
        "Repository", back_populates="webhook_events"
    )
