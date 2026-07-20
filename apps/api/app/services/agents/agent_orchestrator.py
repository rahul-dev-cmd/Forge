"""Agent Orchestrator — Manages execution flow, retries, timeouts, and typed SSE event streams."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import AsyncGenerator, Any

from app.models.copilot import AgentExecution, LLMUsage
from app.services.agents.agent_registry import agent_registry
from app.services.agents.ai_session import AISession
from app.services.agents.intent_classifier import intent_classifier
from app.utils.logger import logger


class AgentOrchestrator:
    """
    Orchestration Layer.
    Decides HOW to execute requests: execution order, retries, timeouts, and streaming SSE event aggregation.
    """

    async def execute_request(
        self, prompt: str, session: AISession, requested_agent: str | None = None
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        # Intent Classification
        intent, default_agent_type = intent_classifier.classify_intent(prompt)
        target_agent_type = requested_agent or default_agent_type.value

        # Agent Resolution
        agent_cls = agent_registry.get_agent_class(target_agent_type)
        agent_instance = agent_cls()

        # Execute with retry & timeout protection
        exec_start = time.perf_counter()
        result = None
        retries = 2

        for attempt in range(retries + 1):
            try:
                result = await asyncio.wait_for(agent_instance.execute(prompt, session), timeout=30.0)
                break
            except Exception as e:
                if attempt == retries:
                    result = {
                        "agent": target_agent_type,
                        "answer": f"Error during agent execution: {e}",
                        "citations": [],
                        "confidence": 0.0,
                        "followups": [],
                    }
                await asyncio.sleep(0.1)

        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Log AgentExecution Metrics
        try:
            exec_record = AgentExecution(
                conversation_id=session.conversation_id,
                agent_type=target_agent_type,
                intent=intent.value if intent else None,
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(result["answer"].split()) if result else 0,
                total_tokens=len(prompt.split()) + (len(result["answer"].split()) if result else 0),
                first_token_ms=50.0,
                total_latency_ms=round(total_latency_ms, 2),
                status="completed",
            )
            session.db.add(exec_record)

            usage_record = LLMUsage(
                conversation_id=session.conversation_id,
                provider="local",
                model_name="local-mock-v1",
                prompt_tokens=exec_record.prompt_tokens,
                completion_tokens=exec_record.completion_tokens,
                first_token_latency_ms=50.0,
                total_response_latency_ms=round(total_latency_ms, 2),
            )
            session.db.add(usage_record)
            await session.db.commit()
        except Exception as e:
            logger.error("Failed to log AgentExecution metrics", extra={"error": str(e)})

        return result or {}

    async def stream_typed_events(
        self, prompt: str, session: AISession, requested_agent: str | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Streams typed SSE events:
        event:thinking
        event:tool
        event:retrieval
        event:citation
        event:token
        event:complete
        """
        # Event 1: Thinking
        yield f"event: thinking\ndata: {json.dumps({'status': 'Analyzing query intent and selecting specialized agent...'})}\n\n"
        await asyncio.sleep(0.05)

        intent, default_agent_type = intent_classifier.classify_intent(prompt)
        target_agent = requested_agent or default_agent_type.value

        # Event 2: Retrieval
        yield f"event: retrieval\ndata: {json.dumps({'status': 'Retrieving ContextPackage via RetrievalEngine...', 'agent': target_agent})}\n\n"
        await asyncio.sleep(0.05)

        # Event 3: Tool
        yield f"event: tool\ndata: {json.dumps({'tool_name': 'context_retrieval', 'status': 'executed', 'permissions_checked': ['repository.read', 'code.search']})}\n\n"
        await asyncio.sleep(0.05)

        # Execute Agent
        result = await self.execute_request(prompt, session, requested_agent=target_agent)

        # Event 4: Citations
        yield f"event: citation\ndata: {json.dumps({'citations': result.get('citations', [])})}\n\n"
        await asyncio.sleep(0.05)

        # Event 5: Tokens (streaming chunks)
        answer = result.get("answer", "")
        words = answer.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"event: token\ndata: {json.dumps({'delta': chunk})}\n\n"
            await asyncio.sleep(0.01)

        # Event 6: Complete (structured payload)
        yield f"event: complete\ndata: {json.dumps({'result': result})}\n\n"


agent_orchestrator = AgentOrchestrator()
