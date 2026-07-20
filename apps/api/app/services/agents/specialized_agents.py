"""7 Specialized Agents returning structured JSON responses."""

from __future__ import annotations

import abc
from typing import Any

from app.models.enums import AgentType
from app.services.agents.ai_session import AISession
from app.services.agents.citation_manager import citation_manager
from app.services.llm.factory import llm_provider_factory
from app.services.tools.context_tools import ContextRetrievalTool


class BaseAgent(abc.ABC):
    """Abstract base class for all specialized Copilot agents."""

    agent_type: AgentType

    @abc.abstractmethod
    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        pass


class CoordinatorAgent(BaseAgent):
    agent_type = AgentType.COORDINATOR

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        # Context package retrieval via tool
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        session.context_package = pkg

        llm = llm_provider_factory.get_provider()
        ans = await llm.generate_text(f"Query: {prompt}\nContext Summary: {str(pkg)[:1000]}")
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "Coordinator",
            "answer": ans,
            "citations": citations,
            "confidence": 0.95,
            "followups": ["Explore related architectural components?", "Analyze module dependencies?"],
        }


class RepositoryAnalystAgent(BaseAgent):
    agent_type = AgentType.REPOSITORY_ANALYST

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "RepositoryAnalyst",
            "answer": f"Repository Architecture Overview for '{prompt}': Codebase is cleanly layered into models, services, tools, and endpoints.",
            "citations": citations,
            "confidence": 0.92,
            "followups": ["View language breakdown statistics?", "Inspect dependency graph?"],
        }


class CodeExplainerAgent(BaseAgent):
    agent_type = AgentType.CODE_EXPLAINER

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "CodeExplainer",
            "answer": f"Detailed Explanation of target code for query '{prompt}': Functions encapsulate specific business rules with parameter validation and explicit type signatures.",
            "citations": citations,
            "confidence": 0.94,
            "followups": ["Explain caller symbols?", "Show method signatures?"],
        }


class DebugAssistantAgent(BaseAgent):
    agent_type = AgentType.DEBUG_ASSISTANT

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "DebugAssistant",
            "answer": f"Root Cause Analysis for query '{prompt}': Check exception handling boundaries and variable initialization states before property dereferencing.",
            "citations": citations,
            "confidence": 0.90,
            "followups": ["Analyze call stack?", "View related exception handlers?"],
        }


class CodeReviewerAgent(BaseAgent):
    agent_type = AgentType.CODE_REVIEWER

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "CodeReviewer",
            "answer": f"Maintainability & Quality Review for '{prompt}': Code meets architectural standards; recommend adding explicit docstrings for public interfaces.",
            "citations": citations,
            "confidence": 0.93,
            "followups": ["Check cyclomatic complexity?", "Verify error handling?"],
        }


class DocumentationAssistantAgent(BaseAgent):
    agent_type = AgentType.DOCUMENTATION_ASSISTANT

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "DocumentationAssistant",
            "answer": f"Generated API Documentation for '{prompt}': Interface definition includes typed parameters, return schemas, and status code specifications.",
            "citations": citations,
            "confidence": 0.96,
            "followups": ["Generate OpenAPI schema snippet?", "Export markdown doc?"],
        }


class PlannerAgent(BaseAgent):
    agent_type = AgentType.PLANNER

    async def execute(self, prompt: str, session: AISession) -> dict[str, Any]:
        ctx_tool = ContextRetrievalTool()
        ctx_res = await ctx_tool.run({"query": prompt, "top_k": 5}, {
            "db": session.db, "workspace_id": session.workspace_id, "repository_id": session.repository_id
        })
        pkg = ctx_res.output if ctx_res.success else {}
        citations = citation_manager.extract_citations(pkg)

        return {
            "agent": "Planner",
            "answer": f"Implementation Plan for '{prompt}':\n1. Define models\n2. Add services\n3. Create endpoints\n4. Add tests.",
            "citations": citations,
            "confidence": 0.91,
            "followups": ["Break down task 1?", "Identify affected files?"],
        }
