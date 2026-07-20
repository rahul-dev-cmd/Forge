"""Context Builder — Standardized RAG ContextPackage Construction."""

from __future__ import annotations

import time
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_knowledge import KnowledgeContext, RetrievalSession, SearchHistory
from app.models.code_intelligence import (
    CallGraph,
    CodeSymbol,
    DependencyGraph,
    ImportGraph,
    IndexedFile,
)
from app.models.repository import Repository
from app.repositories.repository import repository_repository
from app.services.retrieval_engine import retrieval_engine
from app.services.storage_manager import storage_manager
from app.utils.logger import logger


class ContextBuilder:
    """
    Constructs the standardized ContextPackage contract consumed by all future AI Agents (Milestone 9+).
    Expands retrieved chunks with parent classes, child methods, call graph, import graph, and citations.
    """

    async def build_context_package(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        repo_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        user_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        # 1. Fetch Repository
        repo = await repository_repository.get(db, repo_id)
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")

        # 2. Execute Multi-Factor Retrieval
        retrieved_results = await retrieval_engine.search(
            db, workspace_id, repo_id, query, top_k=top_k, search_type="hybrid"
        )

        retrieved_file_paths = list({r.file_path for r in retrieved_results})

        # 3. Expand Related Symbols
        symbols_res = await db.execute(
            select(CodeSymbol, IndexedFile.file_path)
            .join(IndexedFile, CodeSymbol.indexed_file_id == IndexedFile.id)
            .filter(IndexedFile.repository_id == repo_id, IndexedFile.file_path.in_(retrieved_file_paths))
            .limit(30)
        )
        related_symbols: list[dict[str, Any]] = []
        parent_classes: list[str] = []
        child_methods: list[str] = []

        for sym, f_path in symbols_res.all():
            related_symbols.append(
                {
                    "name": sym.name,
                    "fqn": sym.fqn,
                    "symbol_type": sym.symbol_type,
                    "visibility": sym.visibility,
                    "file_path": f_path,
                    "start_line": sym.start_line,
                    "end_line": sym.end_line,
                }
            )
            if sym.symbol_type == "class":
                parent_classes.append(sym.name)
            elif sym.symbol_type == "method":
                child_methods.append(sym.name)

        # 4. Expand Dependency & Import Graphs
        imp_res = await db.execute(
            select(ImportGraph).filter(
                ImportGraph.repository_id == repo_id,
                ImportGraph.source_file_path.in_(retrieved_file_paths),
            )
        )
        imports = [
            {"source_file": i.source_file_path, "target_module": i.target_module}
            for i in imp_res.scalars().all()
        ]

        dep_res = await db.execute(
            select(DependencyGraph).filter(
                DependencyGraph.repository_id == repo_id,
                DependencyGraph.source_path.in_(retrieved_file_paths),
            )
        )
        dependencies = [
            {"source": d.source_path, "target": d.target_path, "type": d.dependency_type}
            for d in dep_res.scalars().all()
        ]

        # 5. Expand Call Graph
        cg_res = await db.execute(
            select(CallGraph).filter(
                CallGraph.repository_id == repo_id,
                CallGraph.caller_file_path.in_(retrieved_file_paths),
            )
        )
        call_graph = [
            {"caller": c.caller_fqn, "callee": c.callee_fqn, "file": c.caller_file_path, "line": c.line_number}
            for c in cg_res.scalars().all()
        ]

        # 6. Read README if available
        repo_dir = storage_manager.get_repo_dir(repo_id)
        readme_text = ""
        for readme_name in ("README.md", "readme.md", "README.txt", "README"):
            readme_path = repo_dir / readme_name
            if readme_path.exists():
                try:
                    readme_text = readme_path.read_text(encoding="utf-8", errors="replace")[:1500]
                    break
                except Exception:
                    pass

        # Calculate Overall Package Confidence
        top_score = retrieved_results[0].final_score if retrieved_results else 0.0
        confidence = min(0.99, max(0.1, top_score / 1.8))

        # Build Standardized ContextPackage
        context_package: dict[str, Any] = {
            "repository": {
                "id": str(repo.id),
                "name": repo.name,
                "full_name": repo.full_name,
                "default_branch": repo.default_branch or "main",
            },
            "workspace": {
                "id": str(workspace_id),
            },
            "query": query,
            "retrievedChunks": [
                {
                    "chunk_id": r.chunk_id,
                    "file_path": r.file_path,
                    "language": r.language,
                    "start_line": r.start_line,
                    "end_line": r.end_line,
                    "content": r.content,
                    "score": r.final_score,
                }
                for r in retrieved_results
            ],
            "relatedSymbols": related_symbols,
            "dependencyGraph": {
                "imports": imports,
                "dependencies": dependencies,
            },
            "files": [
                {"file_path": p, "language": "code"} for p in retrieved_file_paths
            ],
            "metadata": {
                "parent_classes": parent_classes[:10],
                "child_methods": child_methods[:15],
                "call_graph": call_graph[:15],
                "readme_snippet": readme_text,
                "package_metadata": f"Repository {repo.name}",
            },
            "confidence": round(confidence, 2),
            "citations": [
                {
                    "file_path": r.file_path,
                    "start_line": r.start_line,
                    "end_line": r.end_line,
                    "score": r.final_score,
                }
                for r in retrieved_results
            ],
        }

        elapsed = time.perf_counter() - start_time

        # 7. Audit Log Session
        session = RetrievalSession(
            workspace_id=workspace_id,
            repository_id=repo_id,
            user_id=user_id,
            query_text=query,
            top_k=top_k,
            latency_ms=round(elapsed * 1000, 2),
            results_count=len(retrieved_results),
            max_confidence=round(confidence, 2),
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        history = SearchHistory(
            repository_id=repo_id,
            session_id=session.id,
            query=query,
            search_type="hybrid",
            result_count=len(retrieved_results),
            top_similarity_score=retrieved_results[0].vector_score if retrieved_results else 0.0,
            top_bm25_score=retrieved_results[0].bm25_score if retrieved_results else 0.0,
            final_score=top_score,
            duration_ms=round(elapsed * 1000, 2),
        )
        db.add(history)

        k_ctx = KnowledgeContext(
            repository_id=repo_id,
            session_id=session.id,
            query=query,
            confidence=round(confidence, 2),
            package_json=context_package,
        )
        db.add(k_ctx)
        await db.commit()

        logger.info(
            "ContextPackage assembled",
            extra={
                "repo_id": str(repo_id),
                "query": query,
                "confidence": round(confidence, 2),
                "retrieved_count": len(retrieved_results),
            },
        )
        return context_package


context_builder = ContextBuilder()
