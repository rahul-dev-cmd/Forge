"""SQLAlchemy 2.0 ORM Models for Milestone 9 — AI Copilot & Multi-Agent System."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    String,
    ForeignKey,
    UUID,
    Integer,
    DateTime,
    Text,
    Boolean,
    Float,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import AgentType, MessageSender


class Conversation(Base, UUIDMixin, TimestampMixin):
    """
    Stateful AI Copilot conversation session.
    """

    __tablename__ = "conversations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), default="New Conversation", nullable=False)
    active_agent: Mapped[str] = mapped_column(
        String(50), default=AgentType.COORDINATOR.value, nullable=False
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
    summaries: Mapped[list["ConversationSummary"]] = relationship(
        "ConversationSummary", back_populates="conversation", cascade="all, delete-orphan"
    )


class ConversationMessage(Base, UUIDMixin, TimestampMixin):
    """
    Individual message in a conversation.
    """

    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sender: Mapped[str] = mapped_column(String(30), default=MessageSender.USER.value, nullable=False)
    agent_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )

    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class AgentExecution(Base, UUIDMixin, TimestampMixin):
    """
    Log of agent execution runs managed by AgentOrchestrator.
    """

    __tablename__ = "agent_executions"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)

    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    first_token_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="completed", nullable=False)


class ToolInvocation(Base, UUIDMixin, TimestampMixin):
    """
    Log of tool calls executed by ToolExecutor.
    """

    __tablename__ = "tool_invocations"

    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_executions.id", ondelete="CASCADE"), nullable=True
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=dict, nullable=True
    )
    permissions_checked: Mapped[list[str] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), default=list, nullable=True
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromptTemplate(Base, UUIDMixin, TimestampMixin):
    """
    Versioned system & agent prompts.
    """

    __tablename__ = "prompt_templates"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_templates_name_version"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(30), default="v1.0", nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LLMUsage(Base, UUIDMixin, TimestampMixin):
    """
    Detailed AI Observability and metric tracking.
    """

    __tablename__ = "llm_usages"

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    first_token_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_response_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tool_execution_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retrieval_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1 to 5 star rating
    fallback_occurred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ConversationSummary(Base, UUIDMixin, TimestampMixin):
    """
    Hierarchical memory summary of long conversation sessions.
    """

    __tablename__ = "conversation_summaries"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_message_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="summaries")
