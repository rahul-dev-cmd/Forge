"""Code Intelligence REST API router endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.code_intelligence import (
    CallGraph,
    CodeChunk,
    CodeSymbol,
    DependencyGraph,
    ImportGraph,
    IndexedFile,
    IndexJob,
    LanguageStatistic,
    RepositoryIndex,
    RepositoryMetric,
)
from app.models.user import User
from app.repositories.repository import repository_repository
from app.services.indexing_engine import indexing_engine
from app.services.storage_manager import storage_manager
from app.utils.response import wrap_response
from app.workers.queues import enqueue_index

router = APIRouter()


@router.post("/{repository_id}/clone", status_code=status.HTTP_202_ACCEPTED)
async def trigger_clone(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger local repository clone background task."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = IndexJob(
        repository_id=repository_id,
        job_type="repository_clone",
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    arq_id = await enqueue_index("repository_clone", str(repository_id))
    return wrap_response(
        data={"job_id": str(job.id), "arq_job_id": arq_id, "status": "queued"},
        message="Repository clone task queued.",
    )


@router.post("/{repository_id}/index", status_code=status.HTTP_202_ACCEPTED)
async def trigger_index(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger repository AST parsing and symbol extraction pipeline."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = IndexJob(
        repository_id=repository_id,
        job_type="repository_index",
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    arq_id = await enqueue_index("repository_index", str(repository_id), str(job.id))
    return wrap_response(
        data={"job_id": str(job.id), "arq_job_id": arq_id, "status": "queued"},
        message="Repository index pipeline queued.",
    )


@router.post("/{repository_id}/reindex", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reindex(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purge local cache and re-index repository from scratch."""
    repo = await repository_repository.get(db, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = IndexJob(
        repository_id=repository_id,
        job_type="reindex_repository",
        status="queued",
    )
    db.add(job)
    await db.commit()

    arq_id = await enqueue_index("reindex_repository", str(repository_id))
    return wrap_response(
        data={"job_id": str(job.id), "arq_job_id": arq_id, "status": "queued"},
        message="Repository reindex queued.",
    )


@router.get("/{repository_id}/index")
async def get_index_status(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active repository index status."""
    res = await db.execute(
        select(RepositoryIndex)
        .filter(RepositoryIndex.repository_id == repository_id)
        .order_by(desc(RepositoryIndex.created_at))
    )
    idx = res.scalars().first()
    if not idx:
        return wrap_response(data={"repository_id": str(repository_id), "status": "none", "indexed": False})

    return wrap_response(
        data={
            "id": str(idx.id),
            "repository_id": str(idx.repository_id),
            "commit_sha": idx.commit_sha,
            "branch": idx.branch,
            "status": idx.status,
            "ast_version": idx.ast_version,
            "total_files": idx.total_files,
            "total_symbols": idx.total_symbols,
            "total_chunks": idx.total_chunks,
            "total_lines": idx.total_lines,
            "indexed_at": idx.indexed_at.isoformat() if idx.indexed_at else None,
            "error_message": idx.error_message,
        }
    )


@router.get("/{repository_id}/files")
async def list_indexed_files(
    repository_id: uuid.UUID,
    language: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List indexed files for a repository."""
    query = select(IndexedFile).filter(IndexedFile.repository_id == repository_id)
    if language:
        query = query.filter(IndexedFile.language == language.lower())

    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    items = list(res.scalars().all())

    serialized = [
        {
            "id": str(f.id),
            "file_path": f.file_path, # Clean relative path
            "file_hash": f.file_hash,
            "language": f.language,
            "size_bytes": f.size_bytes,
            "line_count": f.line_count,
            "symbol_count": f.symbol_count,
            "chunk_count": f.chunk_count,
            "cyclomatic_complexity": f.cyclomatic_complexity,
            "status": f.status,
        }
        for f in items
    ]
    return wrap_response(data=serialized, page=page, limit=limit)


@router.get("/{repository_id}/tree")
async def get_directory_tree(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get nested directory tree structure of indexed repository files."""
    res = await db.execute(
        select(IndexedFile.file_path, IndexedFile.language, IndexedFile.line_count, IndexedFile.symbol_count)
        .filter(IndexedFile.repository_id == repository_id)
    )
    files = res.all()

    tree: dict[str, Any] = {}
    for path_str, lang, lines, syms in files:
        parts = path_str.split("/")
        curr = tree
        for part in parts[:-1]:
            curr = curr.setdefault(part, {"_type": "dir", "_children": {}})["_children"]
        curr[parts[-1]] = {
            "_type": "file",
            "path": path_str,
            "language": lang,
            "lines": lines,
            "symbols": syms,
        }

    return wrap_response(data=tree)


@router.get("/{repository_id}/symbols")
async def list_symbols(
    repository_id: uuid.UUID,
    query: str | None = Query(None),
    symbol_type: str | None = Query(None),
    language: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search and filter extracted code symbols."""
    q = select(CodeSymbol).filter(CodeSymbol.repository_id == repository_id)
    if symbol_type:
        q = q.filter(CodeSymbol.symbol_type == symbol_type.lower())
    if query:
        q = q.filter(CodeSymbol.name.ilike(f"%{query}%"))

    q = q.offset((page - 1) * limit).limit(limit)
    res = await db.execute(q)
    items = list(res.scalars().all())

    serialized = [
        {
            "id": str(s.id),
            "name": s.name,
            "fqn": s.fqn,
            "symbol_type": s.symbol_type,
            "visibility": s.visibility,
            "modifiers": s.modifiers,
            "signature": s.signature,
            "docstring": s.docstring,
            "start_line": s.start_line,
            "end_line": s.end_line,
            "parameter_count": s.parameter_count,
        }
        for s in items
    ]
    return wrap_response(data=serialized, page=page, limit=limit)


@router.get("/{repository_id}/dependencies")
async def get_dependencies(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get import graphs and dependency graph summary."""
    imports_res = await db.execute(
        select(ImportGraph).filter(ImportGraph.repository_id == repository_id).limit(100)
        )
    imports = list(imports_res.scalars().all())

    deps_res = await db.execute(
        select(DependencyGraph).filter(DependencyGraph.repository_id == repository_id).limit(100)
    )
    deps = list(deps_res.scalars().all())

    return wrap_response(
        data={
            "imports": [
                {
                    "source_file": i.source_file_path,
                    "target_module": i.target_module,
                    "imported_symbols": i.imported_symbols,
                }
                for i in imports
            ],
            "dependencies": [
                {
                    "source": d.source_path,
                    "target": d.target_path,
                    "dependency_type": d.dependency_type,
                }
                for d in deps
            ],
        }
    )


@router.get("/{repository_id}/metrics")
async def get_repository_metrics(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive repository metrics and maintainability index."""
    res = await db.execute(
        select(RepositoryMetric).filter(RepositoryMetric.repository_id == repository_id)
    )
    m = res.scalars().first()
    if not m:
        return wrap_response(data={"repository_id": str(repository_id), "metrics_ready": False})

    return wrap_response(
        data={
            "repository_id": str(m.repository_id),
            "total_files": m.total_files,
            "total_lines": m.total_lines,
            "total_symbols": m.total_symbols,
            "total_chunks": m.total_chunks,
            "average_complexity": m.average_complexity,
            "maintainability_index": m.maintainability_index,
            "largest_file_path": m.largest_file_path,
            "largest_file_bytes": m.largest_file_bytes,
            "deepest_directory_depth": m.deepest_directory_depth,
            "total_classes": m.total_classes,
            "total_functions": m.total_functions,
            "total_methods": m.total_methods,
            "todo_count": m.todo_count,
            "fixme_count": m.fixme_count,
            "documentation_coverage_pct": m.documentation_coverage_pct,
            "language_distribution": m.language_distribution,
        }
    )


@router.get("/{repository_id}/languages")
async def get_language_statistics(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get language distribution statistics for repository."""
    res = await db.execute(
        select(LanguageStatistic)
        .filter(LanguageStatistic.repository_id == repository_id)
        .order_by(desc(LanguageStatistic.percentage))
    )
    stats = list(res.scalars().all())
    return wrap_response(
        data=[
            {
                "language": s.language,
                "file_count": s.file_count,
                "line_count": s.line_count,
                "bytes": s.bytes,
                "percentage": s.percentage,
            }
            for s in stats
        ]
    )


@router.get("/{repository_id}/chunks")
async def list_chunks(
    repository_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pre-embedding code chunk boundaries (no raw content stored)."""
    res = await db.execute(
        select(CodeChunk)
        .filter(CodeChunk.repository_id == repository_id)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    chunks = list(res.scalars().all())
    return wrap_response(
        data=[
            {
                "id": str(c.id),
                "indexed_file_id": str(c.indexed_file_id),
                "branch": c.branch,
                "chunk_hash": c.chunk_hash,
                "chunk_type": c.chunk_type,
                "language": c.language,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "token_estimate": c.token_estimate,
            }
            for c in chunks
        ],
        page=page,
        limit=limit,
    )


@router.get("/{repository_id}/index-jobs")
async def list_index_jobs(
    repository_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List background indexing jobs for repository."""
    res = await db.execute(
        select(IndexJob)
        .filter(IndexJob.repository_id == repository_id)
        .order_by(desc(IndexJob.created_at))
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
                "processed_files": j.processed_files,
                "total_files": j.total_files,
                "error_message": j.error_message,
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "finished_at": j.finished_at.isoformat() if j.finished_at else None,
            }
            for j in jobs
        ]
    )
