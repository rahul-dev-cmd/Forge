"""Tool Taxonomy Base Classes & MCP Integration Interfaces."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class ToolResult:
    success: bool
    output: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(abc.ABC):
    """
    Abstract Base Tool for all AI Copilot agent tools.
    Declares permission requirements for enterprise RBAC.
    """

    name: str
    description: str
    permissions: Sequence[str] = ("repository.read",)

    @abc.abstractmethod
    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        pass


class InternalTool(BaseTool):
    """Internal tool executing within backend service boundaries."""
    pass


class MCPTool(BaseTool):
    """Model Context Protocol (MCP) compatible external tool interface."""
    pass
