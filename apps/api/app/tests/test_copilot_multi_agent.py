"""Tests for Milestone 9 — AI Copilot & Multi-Agent System."""

import uuid
import pytest
from app.models.enums import AgentType, IntentCategory
from app.services.llm.factory import llm_provider_factory
from app.services.tools.tool_executor import tool_executor
from app.services.tools.context_tools import RepositorySearchTool, FileReaderTool
from app.services.agents.agent_registry import agent_registry
from app.services.agents.intent_classifier import intent_classifier
from app.services.agents.ai_session import AISession
from app.services.agents.agent_orchestrator import agent_orchestrator
from app.services.agents.specialized_agents import (
    CoordinatorAgent,
    RepositoryAnalystAgent,
    CodeExplainerAgent,
    DebugAssistantAgent,
    CodeReviewerAgent,
    DocumentationAssistantAgent,
    PlannerAgent,
)


@pytest.mark.asyncio
async def test_llm_provider_factory_and_mock():
    provider = llm_provider_factory.get_provider("local")
    assert provider.get_provider_name() == "local"

    text = await provider.generate_text("Explain architecture")
    assert "Analysis complete" in text

    chunks = []
    async for chunk in provider.stream_text("Explain architecture"):
        chunks.append(chunk)
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_tool_executor_permissions():
    tool = RepositorySearchTool()

    # Denied permission test
    context_denied = {"permissions": ["user.read"]}
    res_denied = await tool_executor.execute_tool(tool, {"query": "test"}, context_denied)
    assert res_denied.success is False
    assert "Permission denied" in res_denied.error


def test_intent_classifier():
    intent1, agent1 = intent_classifier.classify_intent("How do I debug this crash exception?")
    assert intent1 == IntentCategory.DEBUG
    assert agent1 == AgentType.DEBUG_ASSISTANT

    intent2, agent2 = intent_classifier.classify_intent("Review code smells and maintainability")
    assert intent2 == IntentCategory.REVIEW
    assert agent2 == AgentType.CODE_REVIEWER

    intent3, agent3 = intent_classifier.classify_intent("Create a step by step task plan")
    assert intent3 == IntentCategory.PLAN
    assert agent3 == AgentType.PLANNER


@pytest.mark.asyncio
async def test_specialized_agents_registered():
    registered = agent_registry.list_registered_agents()
    assert AgentType.COORDINATOR.value in registered
    assert AgentType.CODE_EXPLAINER.value in registered
    assert AgentType.DEBUG_ASSISTANT.value in registered
    assert AgentType.CODE_REVIEWER.value in registered
    assert AgentType.PLANNER.value in registered


@pytest.mark.asyncio
async def test_typed_sse_event_stream():
    sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        db=None,  # Mocked
    )

    events = []
    async for event_chunk in agent_orchestrator.stream_typed_events("Explain code architecture", sess):
        events.append(event_chunk)

    full_stream = "".join(events)
    assert "event: thinking" in full_stream
    assert "event: retrieval" in full_stream
    assert "event: tool" in full_stream
    assert "event: citation" in full_stream
    assert "event: token" in full_stream
    assert "event: complete" in full_stream
