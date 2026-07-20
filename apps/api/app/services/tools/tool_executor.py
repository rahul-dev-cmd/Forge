"""Tool Executor — Intercepts, validates permissions, and executes tools."""

from __future__ import annotations

import time
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.copilot import ToolInvocation
from app.services.tools.base import BaseTool, ToolResult
from app.utils.logger import logger


class ToolExecutor:
    """
    Decoupled Tool Execution Layer.
    Handles permission validation, retries, duration measurement, and audit logging.
    """

    async def execute_tool(
        self,
        tool: BaseTool,
        kwargs: dict[str, Any],
        context: dict[str, Any],
        db: AsyncSession | None = None,
        execution_id: uuid.UUID | None = None,
    ) -> ToolResult:
        start_time = time.perf_counter()

        # Permission Validation Check
        user_permissions = set(context.get("permissions", ["repository.read", "code.search"]))
        required_perms = set(tool.permissions)

        if not required_perms.issubset(user_permissions):
            missing = list(required_perms - user_permissions)
            logger.warning(
                "Tool permission denied",
                extra={"tool_name": tool.name, "missing_permissions": missing},
            )
            return ToolResult(
                success=False,
                output=None,
                error=f"Permission denied. Required tool permissions: {missing}",
            )

        # Execute Tool with Retry Logic
        result = None
        retries = 2
        for attempt in range(retries + 1):
            try:
                result = await tool.run(kwargs, context)
                if result.success:
                    break
            except Exception as e:
                if attempt == retries:
                    result = ToolResult(success=False, output=None, error=str(e))
                await asyncio.sleep(0.1)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Persist ToolInvocation Metrics
        if db:
            try:
                inv = ToolInvocation(
                    execution_id=execution_id,
                    tool_name=tool.name,
                    arguments_json=kwargs,
                    permissions_checked=list(tool.permissions),
                    result_summary=str(result.output)[:500] if result and result.output else result.error,
                    duration_ms=round(elapsed_ms, 2),
                    success=result.success if result else False,
                )
                db.add(inv)
                await db.commit()
            except Exception as e:
                logger.error("Failed to save ToolInvocation log", extra={"error": str(e)})

        return result or ToolResult(success=False, output=None, error="Unknown tool execution failure")


tool_executor = ToolExecutor()
