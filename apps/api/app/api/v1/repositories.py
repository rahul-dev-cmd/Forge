"""Repository browse, import, sync, and metadata endpoints."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import SyncJobType
from app.models.user import User
from app.services.repository import (
    repository_service,
    RepositoryCreate,
    RepositorySettingsUpdate,
)
from app.services.github_service import (
    github_service,
    RepositoryImportRequest,
    serialize_repository,
)
from app.services.sync_engine import sync_engine
from app.repositories.repository import repository_repository
from app.repositories.sync import repository_sync_repository
from app.repositories.git_metadata import (
    branch_repository,
    commit_repository,
    pull_request_repository,
    issue_repository,
    contributor_repository,
    language_repository,
    topic_repository,
)
from app.utils.validators import validate_repo_url
from app.utils.response import wrap_response

router = APIRouter()


@router.get("")
async def list_repositories(
    project_id: uuid.UUID | None = Query(None, description="Filter by project"),
    workspace_id: uuid.UUID | None = Query(None, description="Filter by workspace"),
    query: str | None = Query(None),
    sync_status: str | None = Query(None),
    sort_by: str = Query("updated_at"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Browse imported repositories with search, filter, sort, and pagination.
    """
    if workspace_id:
        items, total = await repository_repository.list_for_workspace(
            db,
            workspace_id,
            query=query,
            sync_status=sync_status,
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit,
        )
        return wrap_response(
            data=[serialize_repository(r) for r in items],
            page=page,
            limit=limit,
            total=total,
        )

    if project_id:
        items = await repository_service.get_by_project(db, project_id)
        return wrap_response(data=[serialize_repository(r) for r in items])

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide workspace_id or project_id",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def connect_repository(
    repo_in: RepositoryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Legacy metadata connect (clone URL registration). Prefer POST /repositories/import.
    """
    validate_repo_url(repo_in.clone_url, repo_in.provider)
    ip_addr = request.client.host if request.client else None
    repo = await repository_service.create_repository(
        db, repo_in, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data=serialize_repository(repo),
        message="Repository connected successfully.",
    )


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_repository(
    body: RepositoryImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import a repository from a GitHub App installation and queue initial sync.
    """
    result = await github_service.import_repository(
        db, user_id=current_user.id, body=body
    )
    return wrap_response(data=result, message="Repository import started.")


@router.get("/{repository_id}")
async def get_repository_details(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found.")

    languages = await language_repository.list_for_repository(db, repository_id)
    topics = await topic_repository.list_for_repository(db, repository_id)

    data = serialize_repository(repo)
    data["languages"] = [
        {"language": l.language, "bytes": l.bytes, "percentage": l.percentage}
        for l in languages
    ]
    data["topics"] = [t.topic for t in topics]
    return wrap_response(data=data)


@router.post("/{repository_id}/sync")
async def trigger_repository_sync(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    if repo.connection_status == "disconnected":
        raise HTTPException(status_code=400, detail="Repository is disconnected.")

    job = await sync_engine.create_sync_job(
        db,
        repository_id=repo.id,
        job_type=SyncJobType.REPOSITORY_SYNC,
        triggered_by=current_user.id,
        installation_id=repo.installation_id,
    )

    from app.workers.queues import enqueue_sync

    arq_id = await enqueue_sync("repository_sync", str(job.id))
    if arq_id:
        job.arq_job_id = arq_id
        await db.commit()

    return wrap_response(
        data={"sync_job_id": str(job.id), "status": job.status, "arq_job_id": arq_id},
        message="Repository sync queued.",
    )


@router.get("/{repository_id}/status")
async def get_repository_status(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    jobs = await repository_sync_repository.list_for_repository(db, repository_id, limit=10)
    return wrap_response(
        data={
            "repository_id": str(repo.id),
            "connection_status": repo.connection_status,
            "sync_status": repo.sync_status,
            "sync_error": repo.sync_error,
            "last_synced_at": repo.last_synced_at.isoformat() if repo.last_synced_at else None,
            "indexing_ready": repo.indexing_ready,
            "last_webhook_delivery_id": repo.last_webhook_delivery_id,
            "sync_history": [
                {
                    "id": str(j.id),
                    "job_type": j.job_type,
                    "status": j.status,
                    "progress": j.progress,
                    "started_at": j.started_at.isoformat() if j.started_at else None,
                    "finished_at": j.finished_at.isoformat() if j.finished_at else None,
                    "error_message": j.error_message,
                    "branches_synced": j.branches_synced,
                    "commits_synced": j.commits_synced,
                    "pull_requests_synced": j.pull_requests_synced,
                    "issues_synced": j.issues_synced,
                    "contributors_synced": j.contributors_synced,
                }
                for j in jobs
            ],
        }
    )


@router.get("/{repository_id}/branches")
async def list_branches(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    items = await branch_repository.list_for_repository(db, repository_id)
    return wrap_response(
        data=[
            {
                "id": str(b.id),
                "name": b.name,
                "is_default": b.is_default,
                "latest_commit_sha": b.latest_commit_sha,
                "last_synced_at": b.last_synced_at.isoformat() if b.last_synced_at else None,
            }
            for b in items
        ]
    )


@router.get("/{repository_id}/commits")
async def list_commits(
    repository_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    items = await commit_repository.list_for_repository(db, repository_id, limit=limit)
    return wrap_response(
        data=[
            {
                "id": str(c.id),
                "commit_sha": c.commit_sha,
                "author_name": c.author_name,
                "author_login": c.author_login,
                "commit_message": c.commit_message,
                "html_url": c.html_url,
                "additions": c.additions,
                "deletions": c.deletions,
                "committed_at": c.committed_at.isoformat() if c.committed_at else None,
            }
            for c in items
        ]
    )


@router.get("/{repository_id}/pull-requests")
async def list_pull_requests(
    repository_id: uuid.UUID,
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    items = await pull_request_repository.list_for_repository(db, repository_id, limit=limit)
    return wrap_response(
        data=[
            {
                "id": str(pr.id),
                "number": pr.number,
                "title": pr.title,
                "status": pr.status,
                "source_branch": pr.source_branch,
                "target_branch": pr.target_branch,
                "author_login": pr.author_login,
                "author_avatar_url": pr.author_avatar_url,
                "html_url": pr.html_url,
                "draft": pr.draft,
                "updated_at": pr.provider_updated_at.isoformat() if pr.provider_updated_at else None,
            }
            for pr in items
        ]
    )


@router.get("/{repository_id}/issues")
async def list_issues(
    repository_id: uuid.UUID,
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    items = await issue_repository.list_for_repository(db, repository_id, limit=limit)
    return wrap_response(
        data=[
            {
                "id": str(i.id),
                "number": i.number,
                "title": i.title,
                "status": i.status,
                "author_login": i.author_login,
                "html_url": i.html_url,
                "labels": json.loads(i.labels) if i.labels else [],
                "updated_at": i.provider_updated_at.isoformat() if i.provider_updated_at else None,
            }
            for i in items
        ]
    )


@router.get("/{repository_id}/contributors")
async def list_contributors(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    items = await contributor_repository.list_for_repository(db, repository_id)
    return wrap_response(
        data=[
            {
                "id": str(c.id),
                "login": c.login,
                "avatar_url": c.avatar_url,
                "html_url": c.html_url,
                "contributions": c.contributions,
            }
            for c in items
        ]
    )


@router.post("/{repository_id}/disconnect")
async def disconnect_repository(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await github_service.disconnect_repository(
        db, repository_id=repository_id, user_id=current_user.id
    )
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return wrap_response(
        data=serialize_repository(repo),
        message="Repository disconnected.",
    )


@router.patch("/{repository_id}/settings")
async def update_repository_settings(
    repository_id: uuid.UUID,
    settings_in: RepositorySettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    updated = await repository_service.update_settings(
        db, repository_id, settings_in, actor_id=current_user.id, ip_address=ip_addr
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Repository settings not found."
        )
    return wrap_response(
        data={
            "id": str(updated.id),
            "repository_id": str(updated.repository_id),
            "ai_enabled": updated.ai_enabled,
            "indexing_enabled": updated.indexing_enabled,
            "auto_sync": updated.auto_sync,
            "sync_interval": updated.sync_interval,
        },
        message="Repository settings updated successfully.",
    )
