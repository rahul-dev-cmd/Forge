"""Collaboration REST API — Activity feeds, code comments, and notifications."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.collaboration import NotificationRecord, RepositoryComment, WorkspaceActivity
from app.models.user import User

router = APIRouter(tags=["Collaboration & Team Features"])


class CreateCommentRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    line_number: int | None = None
    comment_text: str = Field(..., min_length=1)
    mentions: list[str] = Field(default_factory=list)


@router.get("/workspaces/{id}/activity")
async def get_workspace_activity(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(WorkspaceActivity)
        .filter(WorkspaceActivity.workspace_id == id)
        .order_by(WorkspaceActivity.created_at.desc())
        .limit(50)
    )
    activities = res.scalars().all()
    return {"status": "success", "data": activities}


@router.post("/repositories/{id}/comments")
async def add_repository_comment(
    id: uuid.UUID,
    req: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    comment = RepositoryComment(
        repository_id=id,
        user_id=current_user.id,
        file_path=req.file_path,
        line_number=req.line_number,
        comment_text=req.comment_text,
        mentions=req.mentions,
    )
    db.add(comment)

    # Log activity
    act = WorkspaceActivity(
        workspace_id=current_user.id,  # Fallback
        user_id=current_user.id,
        action="comment_added",
        target_type="repository",
        target_id=str(id),
        metadata_json={"file_path": req.file_path, "mentions": req.mentions},
    )
    db.add(act)
    await db.commit()
    await db.refresh(comment)

    return {"status": "success", "data": comment}


@router.get("/notifications")
async def list_user_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(NotificationRecord)
        .filter(NotificationRecord.user_id == current_user.id)
        .order_by(NotificationRecord.created_at.desc())
    )
    notifications = res.scalars().all()
    return {"status": "success", "data": notifications}
