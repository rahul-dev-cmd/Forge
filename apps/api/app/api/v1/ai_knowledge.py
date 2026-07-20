"""AI Knowledge & RAG Retrieval REST API Router Endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.ai_knowledge import (
    EmbeddingJob,
    EmbeddingVersion,
    KnowledgeContext,
    RepositoryKnowledge,
    RetrievalSession,
    SearchHistory,
)
from app.models.user import User
from app.repositories.repository import repository_repository
from app.services.context_builder import context_builder
from app.services.retrieval_engine import retrieval_engine
from app.utils.response import wrap_response
from app.workers.queues import enqueue_ai

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Semantic or hybrid code search query")
    top_k: int = Field(10, ge=1, le=50)
    search_type: str = Field("hybrid", description="hybrid, semantic, or exact")
    filters: dict[str, Any] | None = None


class ContextRetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Target query for RAG context package construction")
    top_k: int = Field(5, ge=1, le=20)


@router.post("/{repository_id}/embed", status_code=status.HTTP_202_ACCEPTED)
async def trigger_embedding_pipeline(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger background embedding pipeline for a repository."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = EmbeddingJob(
        repository_id=repository_id,
        job_type="repository_embed",
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    arq_id = await enqueue_ai("repository_embed", str(repository_id), str(job.id))
    return wrap_response(
        data={"job_id": str(job.id), "arq_job_id": arq_id, "status": "queued"},
        message="Repository embedding task queued.",
    )


@router.post("/{repository_id}/reembed", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reembed(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purge vectors and re-embed repository from scratch."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = EmbeddingJob(
        repository_id=repository_id,
        job_type="reembed_repository",
        status="queued",
    )
    db.add(job)
    await db.commit()

    arq_id = await enqueue_ai("reembed_repository", str(repository_id))
    return wrap_response(
        data={"job_id": str(job.id), "arq_job_id": arq_id, "status": "queued"},
        message="Repository re-embedding queued.",
    )


@router.get("/{repository_id}/embeddings/status")
async def get_embedding_status(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active embedding status and active collection version."""
    v_res = await db.execute(
        select(EmbeddingVersion)
        .filter(EmbeddingVersion.repository_id == repository_id, EmbeddingVersion.is_active == True)
        .order_by(desc(EmbeddingVersion.created_at))
    )
    active_ver = v_res.scalars().first()

    k_res = await db.execute(
        select(RepositoryKnowledge).filter(RepositoryKnowledge.repository_id == repository_id)
    )
    know = k_res.scalars().first()

    if not active_ver and not know:
        return wrap_response(
            data={"repository_id": str(repository_id), "status": "none", "embedded": False}
        )

    return wrap_response(
        data={
            "repository_id": str(repository_id),
            "status": know.embedding_health if know else "ready",
            "total_vectors": know.total_vectors if know else 0,
            "total_tokens": know.total_tokens if know else 0,
            "provider": know.provider if know else "local",
            "model_name": know.model_name if know else "all-MiniLM-L6-v2",
            "dimensions": know.dimensions if know else 384,
            "commit_sha": active_ver.commit_sha if active_ver else None,
            "version_hash": active_ver.version_hash if active_ver else None,
        }
    )


@router.get("/{repository_id}/knowledge")
async def get_repository_knowledge_summary(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get overall repository knowledge base statistics and cost metrics."""
    k_res = await db.execute(
        select(RepositoryKnowledge).filter(RepositoryKnowledge.repository_id == repository_id)
    )
    know = k_res.scalars().first()
    if not know:
        return wrap_response(data={"repository_id": str(repository_id), "knowledge_ready": False})

    return wrap_response(
        data={
            "repository_id": str(know.repository_id),
            "total_vectors": know.total_vectors,
            "total_tokens": know.total_tokens,
            "estimated_cost_usd": know.estimated_cost_usd,
            "provider": know.provider,
            "model_name": know.model_name,
            "dimensions": know.dimensions,
            "embedding_health": know.embedding_health,
        }
    )


@router.post("/{repository_id}/search")
async def execute_search(
    repository_id: uuid.UUID,
    body: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute semantic or multi-factor hybrid search."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    results = await retrieval_engine.search(
        db,
        workspace_id=repo.workspace_id,
        repo_id=repository_id,
        query=body.query,
        top_k=body.top_k,
        search_type=body.search_type,
        filters=body.filters,
    )

    serialized = [
        {
            "chunk_id": r.chunk_id,
            "file_path": r.file_path,
            "language": r.language,
            "start_line": r.start_line,
            "end_line": r.end_line,
            "content": r.content,
            "vector_score": r.vector_score,
            "bm25_score": r.bm25_score,
            "symbol_bonus": r.symbol_bonus,
            "dependency_bonus": r.dependency_bonus,
            "final_score": r.final_score,
            "symbols": r.symbols,
        }
        for r in results
    ]
    return wrap_response(data=serialized)


@router.post("/{repository_id}/retrieve-context")
async def retrieve_context_package(
    repository_id: uuid.UUID,
    body: ContextRetrieveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate standardized ContextPackage data contract for RAG."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    pkg = await context_builder.build_context_package(
        db,
        workspace_id=repo.workspace_id,
        repo_id=repository_id,
        query=body.query,
        top_k=body.top_k,
        user_id=current_user.id,
    )
    return wrap_response(data=pkg)


@router.get("/{repository_id}/embedding-jobs")
async def list_embedding_jobs(
    repository_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List background embedding jobs for repository."""
    res = await db.execute(
        select(EmbeddingJob)
        .filter(EmbeddingJob.repository_id == repository_id)
        .order_by(desc(EmbeddingJob.created_at))
        .limit(limit)
    )
    jobs = list(res.scalars().all())
    return wrap_response(
        data=[
            {
                "id": str(j.id),
                "job_type": j.job_type,
                "status": j.status,
                "progress_pct": j.progress_pct,
                "processed_chunks": j.processed_chunks,
                "total_chunks": j.total_chunks,
                "tokens_processed": j.tokens_processed,
                "estimated_cost_usd": j.estimated_cost_usd,
                "error_message": j.error_message,
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "finished_at": j.finished_at.isoformat() if j.finished_at else None,
            }
            for j in jobs
        ]
    )


@router.get("/{repository_id}/search-history")
async def list_search_history(
    repository_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List search query history and latencies."""
    res = await db.execute(
        select(SearchHistory)
        .filter(SearchHistory.repository_id == repository_id)
        .order_by(desc(SearchHistory.created_at))
        .limit(limit)
    )
    histories = list(res.scalars().all())
    return wrap_response(
        data=[
            {
                "id": str(h.id),
                "query": h.query,
                "search_type": h.search_type,
                "result_count": h.result_count,
                "top_similarity_score": h.top_similarity_score,
                "top_bm25_score": h.top_bm25_score,
                "final_score": h.final_score,
                "duration_ms": h.duration_ms,
                "created_at": h.created_at.isoformat(),
            }
            for h in histories
        ]
    )
