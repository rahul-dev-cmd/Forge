"""Embedding Pipeline — Vector Generation, Deduplication, and Qdrant Indexing."""

from __future__ import annotations

import hashlib
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.ai_knowledge import (
    EmbeddingJob,
    EmbeddingRecord,
    EmbeddingVersion,
    RepositoryKnowledge,
)
from app.models.code_intelligence import (
    CodeChunk,
    CodeSymbol,
    IndexedFile,
    RepositoryIndex,
    RepositorySnapshot,
)
from app.models.enums import EmbeddingJobType, EmbeddingStatus
from app.models.repository import Repository
from app.repositories.repository import repository_repository
from app.services.embedding.factory import embedding_provider_factory
from app.services.storage_manager import storage_manager
from app.services.vector_db.base import VectorPoint
from app.services.vector_db.factory import vector_db_factory
from app.utils.logger import logger


class EmbeddingPipeline:
    """
    Orchestrates CodeChunk extraction, embedding generation, vector DB upsert, and metrics tracking.
    """

    async def run_embedding_pipeline(
        self, db: AsyncSession, repo_id: uuid.UUID, job_id: uuid.UUID | None = None
    ) -> RepositoryKnowledge:
        start_time = time.perf_counter()

        # 1. Fetch Repository model
        repo = await repository_repository.get(db, repo_id)
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")

        workspace_id = repo.workspace_id

        # 2. Resolve latest RepositoryIndex and Snapshot
        idx_res = await db.execute(
            select(RepositoryIndex)
            .filter(RepositoryIndex.repository_id == repo_id, RepositoryIndex.status == "completed")
            .order_by(RepositoryIndex.created_at.desc())
        )
        repo_index = idx_res.scalars().first()
        if not repo_index:
            raise ValueError(f"No completed index found for repository {repo_id}. Run indexing first.")

        snap_res = await db.execute(
            select(RepositorySnapshot).filter(RepositorySnapshot.id == repo_index.snapshot_id)
        )
        snapshot = snap_res.scalars().first()
        snapshot_id = snapshot.id if snapshot else repo_index.id

        # 3. Resolve EmbeddingJob
        job = None
        if job_id:
            j_res = await db.execute(select(EmbeddingJob).filter(EmbeddingJob.id == job_id))
            job = j_res.scalars().first()

        if not job:
            job = EmbeddingJob(
                repository_id=repo_id,
                job_type=EmbeddingJobType.REPOSITORY_EMBED.value,
                status=EmbeddingStatus.PROCESSING.value,
                started_at=datetime.now(timezone.utc),
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
        else:
            job.status = EmbeddingStatus.PROCESSING.value
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

        # 4. Fetch all CodeChunks for this repository index
        chunks_res = await db.execute(
            select(CodeChunk, IndexedFile)
            .join(IndexedFile, CodeChunk.indexed_file_id == IndexedFile.id)
            .filter(CodeChunk.repository_id == repo_id)
        )
        rows = chunks_res.all()
        total_chunks = len(rows)
        job.total_chunks = total_chunks
        db.add(job)
        await db.commit()

        if total_chunks == 0:
            job.status = EmbeddingStatus.COMPLETED.value
            job.progress_pct = 100.0
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

        # 5. Resolve Embedding & Vector DB Providers
        embed_provider = embedding_provider_factory.get_provider()
        vector_db = vector_db_factory.get_provider()

        collection_name = settings.QDRANT_COLLECTION_NAME
        dimensions = embed_provider.get_dimensions()
        await vector_db.create_collection(collection_name, dimensions)

        repo_dir = storage_manager.get_repo_dir(repo_id)

        batch_size = settings.EMBEDDING_BATCH_SIZE
        processed_chunks = 0
        total_tokens = 0
        vector_points: list[VectorPoint] = []
        new_records: list[EmbeddingRecord] = []

        for i in range(0, total_chunks, batch_size):
            batch = rows[i : i + batch_size]
            batch_texts: list[str] = []
            batch_metadata: list[dict] = []

            for chunk, indexed_file in batch:
                # Read source text from Git clone
                rel_path = indexed_file.file_path
                abs_path = repo_dir / rel_path

                chunk_text = f"File: {rel_path}\nLanguage: {chunk.language}\n"
                try:
                    lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    extracted_lines = lines[chunk.start_line - 1 : chunk.end_line]
                    chunk_text += "\n".join(extracted_lines)
                except Exception:
                    chunk_text += f"# Chunk lines {chunk.start_line}-{chunk.end_line}"

                # Calculate context-aware deduplication hash
                raw_context = f"{repo_id}:{chunk.branch}:{rel_path}:{chunk.start_line}:{chunk.end_line}:{chunk.chunk_hash}"
                context_hash = hashlib.sha256(raw_context.encode("utf-8")).hexdigest()

                vector_id = str(uuid.uuid5(uuid.NAMESPACE_URL, context_hash))
                est_tokens = max(1, len(chunk_text) // 4)
                total_tokens += est_tokens

                is_test = "test" in rel_path.lower() or "spec" in rel_path.lower()

                payload = {
                    "vector_id": vector_id,
                    "workspace_id": str(workspace_id),
                    "repository_id": str(repo_id),
                    "snapshot_id": str(snapshot_id),
                    "chunk_id": str(chunk.id),
                    "file_path": rel_path,
                    "language": chunk.language,
                    "chunk_type": chunk.chunk_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "is_test_file": is_test,
                    "repository_version": repo_index.ast_version,
                    "context_hash": context_hash,
                }

                batch_texts.append(chunk_text)
                batch_metadata.append(
                    {
                        "vector_id": vector_id,
                        "chunk_id": chunk.id,
                        "context_hash": context_hash,
                        "payload": payload,
                        "token_count": est_tokens,
                    }
                )

            # Generate vectors
            embeddings = await embed_provider.embed_texts(batch_texts)

            for meta, emb in zip(batch_metadata, embeddings):
                vector_points.append(
                    VectorPoint(id=meta["vector_id"], vector=emb, payload=meta["payload"])
                )
                new_records.append(
                    EmbeddingRecord(
                        repository_id=repo_id,
                        snapshot_id=snapshot_id,
                        chunk_id=meta["chunk_id"],
                        vector_id=meta["vector_id"],
                        context_hash=meta["context_hash"],
                        provider=embed_provider.get_model_name(),
                        model_name=embed_provider.get_model_name(),
                        dimensions=dimensions,
                        token_count=meta["token_count"],
                    )
                )

            processed_chunks += len(batch)
            job.processed_chunks = processed_chunks
            job.progress_pct = (processed_chunks / max(1, total_chunks)) * 100.0
            job.tokens_processed = total_tokens
            db.add(job)
            await db.commit()

        # 6. Upsert vectors to vector DB
        if vector_points:
            await vector_db.upsert_vectors(collection_name, vector_points)

        # 7. Persist EmbeddingRecord entries
        await db.execute(
            delete(EmbeddingRecord).filter(EmbeddingRecord.repository_id == repo_id)
        )
        for rec in new_records:
            db.add(rec)

        # 8. Create/Update EmbeddingVersion
        version_hash = hashlib.sha256(
            f"{repo_id}:{snapshot_id}:{embed_provider.get_model_name()}".encode("utf-8")
        ).hexdigest()

        version_query = select(EmbeddingVersion).filter(
            EmbeddingVersion.repository_id == repo_id, EmbeddingVersion.version_hash == version_hash
        )
        v_res = await db.execute(version_query)
        emb_ver = v_res.scalars().first()
        if not emb_ver:
            emb_ver = EmbeddingVersion(
                repository_id=repo_id,
                snapshot_id=snapshot_id,
                commit_sha=repo_index.commit_sha,
                branch=repo_index.branch,
                version_hash=version_hash,
                provider=embed_provider.get_model_name(),
                model_name=embed_provider.get_model_name(),
                dimensions=dimensions,
                vector_count=len(vector_points),
                is_active=True,
            )
            db.add(emb_ver)

        # 9. Update RepositoryKnowledge metrics
        k_query = select(RepositoryKnowledge).filter(RepositoryKnowledge.repository_id == repo_id)
        k_res = await db.execute(k_query)
        know = k_res.scalars().first()
        if not know:
            know = RepositoryKnowledge(repository_id=repo_id)

        know.total_vectors = len(vector_points)
        know.total_tokens = total_tokens
        know.provider = settings.EMBEDDING_PROVIDER
        know.model_name = embed_provider.get_model_name()
        know.dimensions = dimensions
        know.embedding_health = "ready"
        db.add(know)

        # 10. Mark Job Complete
        job.status = EmbeddingStatus.COMPLETED.value
        job.progress_pct = 100.0
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)

        await db.commit()

        elapsed = time.perf_counter() - start_time
        logger.info(
            "Embedding pipeline complete",
            extra={
                "repo_id": str(repo_id),
                "total_vectors": len(vector_points),
                "total_tokens": total_tokens,
                "elapsed_sec": round(elapsed, 2),
            },
        )
        return know


embedding_pipeline = EmbeddingPipeline()
