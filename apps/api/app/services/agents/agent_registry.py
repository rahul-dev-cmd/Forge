"""Agent Registry — Dynamic Registration and Lookup for Copilot Agents."""

from __future__ import annotations

from typing import Type, Dict
from app.models.enums import AgentType


class AgentRegistry:
    """Registry maintaining specialized agent implementations."""

    def __init__(self):
        self._registry: Dict[str, Type] = {}

    def register_agent(self, agent_type: str | AgentType, agent_class: Type) -> None:
        key = agent_type.value if isinstance(agent_type, AgentType) else str(agent_type)
        self._registry[key] = agent_class

    def get_agent_class(self, agent_type: str | AgentType) -> Type:
        key = agent_type.value if isinstance(agent_type, AgentType) else str(agent_type)
        if key not in self._registry:
            # Fallback to Coordinator if agent type is unknown
            key = AgentType.COORDINATOR.value
        return self._registry[key]

    def list_registered_agents(self) -> list[str]:
        return list(self._registry.keys())


agent_registry = AgentRegistry()

from app.services.agents.specialized_agents import (
    CoordinatorAgent,
    RepositoryAnalystAgent,
    CodeExplainerAgent,
    DebugAssistantAgent,
    CodeReviewerAgent,
    DocumentationAssistantAgent,
    PlannerAgent,
)

agent_registry.register_agent(AgentType.COORDINATOR, CoordinatorAgent)
agent_registry.register_agent(AgentType.REPOSITORY_ANALYST, RepositoryAnalystAgent)
agent_registry.register_agent(AgentType.CODE_EXPLAINER, CodeExplainerAgent)
agent_registry.register_agent(AgentType.DEBUG_ASSISTANT, DebugAssistantAgent)
agent_registry.register_agent(AgentType.CODE_REVIEWER, CodeReviewerAgent)
agent_registry.register_agent(AgentType.DOCUMENTATION_ASSISTANT, DocumentationAssistantAgent)
agent_registry.register_agent(AgentType.PLANNER, PlannerAgent)

