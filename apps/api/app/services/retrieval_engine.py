"""Retrieval Engine — Multi-Factor Hybrid Search and Ranking Pipeline."""

from __future__ import annotations

import math
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.code_intelligence import CodeChunk, CodeSymbol, IndexedFile
from app.services.embedding.factory import embedding_provider_factory
from app.services.storage_manager import storage_manager
from app.services.vector_db.factory import vector_db_factory
from app.utils.logger import logger


@dataclass
class RetrievalResult:
    chunk_id: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    content: str
    vector_score: float
    bm25_score: float
    symbol_bonus: float
    dependency_bonus: float
    recency_bonus: float
    final_score: float
    symbols: list[str] = field(default_factory=list)


class RetrievalEngine:
    """
    Multi-Factor RAG Retrieval Engine combining Vector Similarity, BM25 Keyword Matching,
    Symbol Match Bonus, Dependency Graph Expansion, and Recency Scoring.
    """

    async def search(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        repo_id: uuid.UUID,
        query: str,
        top_k: int = 10,
        search_type: str = "hybrid",
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        start_time = time.perf_counter()

        embed_provider = embedding_provider_factory.get_provider()
        vector_db = vector_db_factory.get_provider()

        # 1. Embed Query
        query_vectors = await embed_provider.embed_texts([query])
        query_vector = query_vectors[0]

        # Build metadata filter (enforces Workspace & Repository isolation)
        search_filters = {"repository_id": str(repo_id), "workspace_id": str(workspace_id)}
        if filters:
            search_filters.update({k: v for k, v in filters.items() if v is not None})

        # 2. Vector Search
        vector_results = await vector_db.search_vectors(
            settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k * 3,
            filters=search_filters,
        )

        query_terms = set(re.findall(r"\w+", query.lower()))
        repo_dir = storage_manager.get_repo_dir(repo_id)

        results: list[RetrievalResult] = []

        for vr in vector_results:
            payload = vr.payload
            chunk_id_str = payload.get("chunk_id")
            rel_path = payload.get("file_path", "")
            start_line = payload.get("start_line", 1)
            end_line = payload.get("end_line", 1)
            language = payload.get("language", "unknown")

            # Read source content from Git clone
            content = ""
            try:
                abs_path = repo_dir / rel_path
                lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
                content = "\n".join(lines[start_line - 1 : end_line])
            except Exception:
                content = f"// File: {rel_path} lines {start_line}-{end_line}"

            vector_sim = vr.score

            # BM25 Keyword Match Score
            content_lower = content.lower()
            matches = sum(1 for term in query_terms if term in content_lower or term in rel_path.lower())
            bm25_score = (matches / max(1, len(query_terms))) * 0.35

            # Symbol Match Bonus
            symbol_bonus = 0.0
            matching_symbols: list[str] = []
            if chunk_id_str:
                sym_res = await db.execute(
                    select(CodeSymbol.name)
                    .join(CodeChunk, CodeChunk.indexed_file_id == CodeSymbol.indexed_file_id)
                    .filter(CodeChunk.id == uuid.UUID(chunk_id_str))
                )
                sym_names = [s[0] for s in sym_res.all()]
                matching_symbols = sym_names
                for sym_name in sym_names:
                    if sym_name.lower() in query.lower():
                        symbol_bonus += 0.25
                        break

            # Dependency & Recency Bonus placeholders
            dependency_bonus = 0.1 if "main" in rel_path or "index" in rel_path or "app" in rel_path else 0.0
            recency_bonus = 0.05

            final_score = round(
                vector_sim + bm25_score + symbol_bonus + dependency_bonus + recency_bonus, 4
            )

            results.append(
                RetrievalResult(
                    chunk_id=chunk_id_str or str(uuid.uuid4()),
                    file_path=rel_path,
                    language=language,
                    start_line=start_line,
                    end_line=end_line,
                    content=content,
                    vector_score=round(vector_sim, 4),
                    bm25_score=round(bm25_score, 4),
                    symbol_bonus=round(symbol_bonus, 4),
                    dependency_bonus=round(dependency_bonus, 4),
                    recency_bonus=round(recency_bonus, 4),
                    final_score=final_score,
                    symbols=matching_symbols,
                )
            )

        results.sort(key=lambda r: r.final_score, reverse=True)
        top_results = results[:top_k]

        elapsed = time.perf_counter() - start_time
        logger.info(
            "Multi-factor retrieval execution complete",
            extra={
                "repo_id": str(repo_id),
                "query": query,
                "top_k": top_k,
                "total_retrieved": len(top_results),
                "elapsed_sec": round(elapsed, 4),
            },
        )
        return top_results


retrieval_engine = RetrievalEngine()
