import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import WorkspaceRoleChecker
from app.models.user import User
from app.models.enums import WorkspaceRole
from app.models.audit_log import AuditLog
from app.models.activity import RepositoryActivity
from app.models.project import Project
from app.models.repository import Repository
from app.utils.response import wrap_response

router = APIRouter()

# Role guard: Workspace members can view activities
require_workspace_viewer = WorkspaceRoleChecker([
    WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER
])

@router.get("/workspace/{workspace_id}")
async def get_workspace_activity_timeline(
    workspace_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_workspace_viewer)
):
    """
    Retrieve unified workspace activity feed, combining audit logs and repository activities.
    Includes workspace-scoped audits and audits for projects belonging to the workspace.
    """
    # Resolve project IDs in this workspace for related audit events
    project_ids_res = await db.execute(
        select(Project.id).filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at == None,
        )
    )
    project_ids = list(project_ids_res.scalars().all())

    audit_filters = [
        (AuditLog.target_type == "workspace") & (AuditLog.target_id == workspace_id),
    ]
    if project_ids:
        audit_filters.append(
            (AuditLog.target_type == "project") & (AuditLog.target_id.in_(project_ids))
        )

    audit_query = (
        select(AuditLog)
        .filter(or_(*audit_filters))
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
    )
    audit_res = await db.execute(audit_query)
    audits = list(audit_res.scalars().all())

    repo_act_query = (
        select(RepositoryActivity)
        .join(Repository)
        .filter(Repository.workspace_id == workspace_id)
        .order_by(desc(RepositoryActivity.created_at))
        .limit(limit)
    )
    repo_act_res = await db.execute(repo_act_query)
    repo_activities = list(repo_act_res.scalars().all())

    combined = []
    for log in audits:
        combined.append({
            "id": str(log.id),
            "type": "audit",
            "action": log.action,
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "created_at": log.created_at.isoformat(),
            "details": log.details
        })

    for act in repo_activities:
        combined.append({
            "id": str(act.id),
            "type": "repository",
            "action": act.activity_type,
            "actor_id": str(act.actor_id),
            "created_at": act.created_at.isoformat(),
            "details": act.activity_metadata
        })

    combined.sort(key=lambda x: x["created_at"], reverse=True)
    return wrap_response(data=combined[:limit])
