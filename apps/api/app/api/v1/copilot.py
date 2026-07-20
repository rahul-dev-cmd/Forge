"""FastAPI REST Router for AI Copilot & Multi-Agent System."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.models.copilot import Conversation, ConversationMessage
from app.models.enums import AgentType, MessageSender
from app.models.user import User
from app.services.agents.agent_orchestrator import agent_orchestrator
from app.services.agents.ai_session import AISession
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/ai", tags=["ai-copilot"])


# Schemas
class CreateConversationRequest(BaseModel):
    workspace_id: uuid.UUID
    repository_id: uuid.UUID | None = None
    title: str = "New Conversation"
    active_agent: str = AgentType.COORDINATOR.value


class ChatMessageRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    workspace_id: uuid.UUID
    repository_id: uuid.UUID | None = None
    agent: str | None = None
    conversation_id: uuid.UUID | None = None


class StandardAgentRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    workspace_id: uuid.UUID
    repository_id: uuid.UUID | None = None


# Endpoints
@router.post("/chat")
async def chat_stream(
    req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Typed Server-Sent Events (SSE) Streaming Endpoint.
    Streams event:thinking, event:retrieval, event:tool, event:citation, event:token, event:complete.
    """
    conv_id = req.conversation_id
    if not conv_id:
        conv = Conversation(
            workspace_id=req.workspace_id,
            repository_id=req.repository_id,
            user_id=current_user.id,
            title=req.prompt[:40] + "...",
            active_agent=req.agent or AgentType.COORDINATOR.value,
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    # Record User Message
    user_msg = ConversationMessage(
        conversation_id=conv_id,
        sender=MessageSender.USER.value,
        content=req.prompt,
        tokens_used=len(req.prompt.split()),
    )
    db.add(user_msg)
    await db.commit()

    ai_sess = AISession(
        conversation_id=conv_id,
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
        active_agent=req.agent or AgentType.COORDINATOR.value,
    )

    async def event_generator():
        async for sse_chunk in agent_orchestrator.stream_typed_events(req.prompt, ai_sess, requested_agent=req.agent):
            yield sse_chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/explain")
async def explain_code(
    req: StandardAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
    )
    res = await agent_orchestrator.execute_request(req.prompt, ai_sess, requested_agent=AgentType.CODE_EXPLAINER.value)
    return {"status": "success", "data": res}


@router.post("/review")
async def review_code(
    req: StandardAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
    )
    res = await agent_orchestrator.execute_request(req.prompt, ai_sess, requested_agent=AgentType.CODE_REVIEWER.value)
    return {"status": "success", "data": res}


@router.post("/debug")
async def debug_code(
    req: StandardAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
    )
    res = await agent_orchestrator.execute_request(req.prompt, ai_sess, requested_agent=AgentType.DEBUG_ASSISTANT.value)
    return {"status": "success", "data": res}


@router.post("/plan")
async def plan_task(
    req: StandardAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
    )
    res = await agent_orchestrator.execute_request(req.prompt, ai_sess, requested_agent=AgentType.PLANNER.value)
    return {"status": "success", "data": res}


@router.post("/summarize")
async def summarize_repo(
    req: StandardAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_sess = AISession(
        conversation_id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        db=db,
    )
    res = await agent_orchestrator.execute_request(req.prompt, ai_sess, requested_agent=AgentType.REPOSITORY_ANALYST.value)
    return {"status": "success", "data": res}


# Conversation CRUD
@router.get("/conversations")
async def list_conversations(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Conversation)
        .filter(Conversation.workspace_id == workspace_id, Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )
    convs = res.scalars().all()
    return {"status": "success", "data": convs}


@router.post("/conversations")
async def create_conversation(
    req: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(
        workspace_id=req.workspace_id,
        repository_id=req.repository_id,
        user_id=current_user.id,
        title=req.title,
        active_agent=req.active_agent,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {"status": "success", "data": conv}


@router.get("/conversations/{id}")
async def get_conversation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Conversation).filter(Conversation.id == id, Conversation.user_id == current_user.id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_res = await db.execute(
        select(ConversationMessage).filter(ConversationMessage.conversation_id == id).order_by(ConversationMessage.created_at.asc())
    )
    messages = msg_res.scalars().all()

    return {
        "status": "success",
        "data": {
            "id": conv.id,
            "title": conv.title,
            "workspace_id": conv.workspace_id,
            "repository_id": conv.repository_id,
            "active_agent": conv.active_agent,
            "messages": messages,
        },
    }


@router.post("/conversations/{id}/messages")
async def add_message(
    id: uuid.UUID,
    req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    msg = ConversationMessage(
        conversation_id=id,
        sender=MessageSender.USER.value,
        content=req.prompt,
        tokens_used=len(req.prompt.split()),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"status": "success", "data": msg}


@router.delete("/conversations/{id}")
async def delete_conversation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Conversation).filter(Conversation.id == id, Conversation.user_id == current_user.id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conv)
    await db.commit()
    return {"status": "success", "message": "Conversation deleted"}
