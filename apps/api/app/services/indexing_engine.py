"""Indexing Engine — Resumable Codebase Indexing Pipeline and Graph Construction."""

from __future__ import annotations

import hashlib
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.code_intelligence import (
    CallGraph,
    CodeChunk,
    CodeReference,
    CodeSymbol,
    DependencyGraph,
    ImportGraph,
    IndexCheckpoint,
    IndexedFile,
    IndexJob,
    LanguageStatistic,
    RepositoryIndex,
    RepositoryMetric,
    RepositorySnapshot,
)
from app.models.enums import IndexJobType, IndexStatus, SyncStatus
from app.models.repository import Repository
from app.repositories.repository import repository_repository
from app.services.parser.manager import parser_manager
from app.services.storage_manager import storage_manager
from app.utils.logger import logger


class IndexingEngine:
    """
    Resumable Code Indexing Pipeline & Knowledge Graph Builder.
    """

    async def run_indexing_pipeline(
        self, db: AsyncSession, repo_id: uuid.UUID, job_id: uuid.UUID | None = None
    ) -> RepositoryIndex:
        start_time = time.perf_counter()

        # 1. Fetch Repository model
        repo = await repository_repository.get(db, repo_id)
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")

        # 2. Local clone / pull
        repo_dir = storage_manager.clone_repository(repo_id, repo.clone_url)
        commit_sha = storage_manager.get_current_commit_sha(repo_id)

        # 3. Create or resolve RepositorySnapshot
        snapshot_query = select(RepositorySnapshot).filter(
            RepositorySnapshot.repository_id == repo_id,
            RepositorySnapshot.commit_sha == commit_sha,
        )
        snap_res = await db.execute(snapshot_query)
        snapshot = snap_res.scalars().first()
        if not snapshot:
            snapshot = RepositorySnapshot(
                repository_id=repo_id,
                commit_sha=commit_sha,
                branch=repo.default_branch or "main",
                repository_version=1,
            )
            db.add(snapshot)
            await db.commit()
            await db.refresh(snapshot)

        # 4. Resolve or create RepositoryIndex
        index_query = select(RepositoryIndex).filter(
            RepositoryIndex.repository_id == repo_id,
            RepositoryIndex.commit_sha == commit_sha,
        )
        idx_res = await db.execute(index_query)
        repo_index = idx_res.scalars().first()
        if not repo_index:
            repo_index = RepositoryIndex(
                repository_id=repo_id,
                snapshot_id=snapshot.id,
                commit_sha=commit_sha,
                branch=repo.default_branch or "main",
                status=IndexStatus.RUNNING.value,
            )
            db.add(repo_index)
            await db.commit()
            await db.refresh(repo_index)
        else:
            repo_index.status = IndexStatus.RUNNING.value
            db.add(repo_index)
            await db.commit()

        # 5. Handle IndexJob tracking
        job = None
        if job_id:
            job_query = select(IndexJob).filter(IndexJob.id == job_id)
            j_res = await db.execute(job_query)
            job = j_res.scalars().first()

        if not job:
            job = IndexJob(
                repository_id=repo_id,
                job_type=IndexJobType.REPOSITORY_INDEX.value,
                status=IndexStatus.RUNNING.value,
                started_at=datetime.now(timezone.utc),
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
        else:
            job.status = IndexStatus.RUNNING.value
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

        # 6. List indexable files
        files_to_index = storage_manager.list_indexable_files(repo_id)
        total_files_count = len(files_to_index)
        job.total_files = total_files_count
        db.add(job)
        await db.commit()

        # 7. Checkpoint setup for resumability
        cp_query = select(IndexCheckpoint).filter(
            IndexCheckpoint.repository_id == repo_id, IndexCheckpoint.job_id == job.id
        )
        cp_res = await db.execute(cp_query)
        checkpoint = cp_res.scalars().first()
        if not checkpoint:
            checkpoint = IndexCheckpoint(
                repository_id=repo_id,
                job_id=job.id,
                processed_files_count=0,
            )
            db.add(checkpoint)
            await db.commit()
            await db.refresh(checkpoint)

        last_processed = checkpoint.last_processed_file
        skip_mode = bool(last_processed)

        # Aggregate metric accumulators
        total_lines = 0
        total_symbols = 0
        total_chunks = 0
        total_complexity = 0
        max_complexity = 1
        largest_file_path = None
        largest_file_bytes = 0
        deepest_dir_depth = 0
        total_classes = 0
        total_functions = 0
        total_methods = 0
        todo_count = 0
        fixme_count = 0
        docstring_count = 0

        lang_stats: dict[str, dict[str, int]] = {}

        processed_count = checkpoint.processed_files_count

        # Pre-fetch existing indexed files for diff-based incremental re-use
        prev_idx_res = await db.execute(
            select(IndexedFile).filter(IndexedFile.repository_id == repo_id)
        )
        existing_file_cache = {f.file_path: f for f in prev_idx_res.scalars().all()}

        for rel_path, abs_path in files_to_index:
            if skip_mode:
                if rel_path == last_processed:
                    skip_mode = False
                continue

            try:
                content = abs_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            file_size = abs_path.stat().st_size
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Incremental Optimization: Check if file hash is identical to previous index
            prev_file = existing_file_cache.get(rel_path)
            if prev_file and prev_file.file_hash == file_hash:
                # Reuse existing file metrics without re-parsing AST
                symbol_count = prev_file.symbol_count
                chunk_count = prev_file.chunk_count
                complexity = prev_file.cyclomatic_complexity
                language = prev_file.language
                line_count = prev_file.line_count

                idx_file = IndexedFile(
                    repository_id=repo_id,
                    index_id=repo_index.id,
                    file_path=rel_path,
                    file_hash=file_hash,
                    language=language,
                    size_bytes=file_size,
                    line_count=line_count,
                    symbol_count=symbol_count,
                    chunk_count=chunk_count,
                    cyclomatic_complexity=complexity,
                    status=IndexStatus.COMPLETED.value,
                )
                db.add(idx_file)
                await db.commit()
                await db.refresh(idx_file)

                total_lines += line_count
                total_symbols += symbol_count
                total_chunks += chunk_count
                total_complexity += complexity
                processed_count += 1
                checkpoint.last_processed_file = rel_path
                checkpoint.processed_files_count = processed_count
                db.add(checkpoint)
                await db.commit()
                continue

            parsed = parser_manager.parse_file(rel_path, content)

            if file_size > largest_file_bytes:
                largest_file_bytes = file_size
                largest_file_path = rel_path

            dir_depth = len(Path(rel_path).parts) - 1
            if dir_depth > deepest_dir_depth:
                deepest_dir_depth = dir_depth

            # Create IndexedFile
            idx_file = IndexedFile(
                repository_id=repo_id,
                index_id=repo_index.id,
                file_path=rel_path,
                file_hash=file_hash,
                language=parsed.language,
                size_bytes=file_size,
                line_count=parsed.line_count,
                symbol_count=parsed.symbol_count,
                chunk_count=parsed.chunk_count,
                cyclomatic_complexity=parsed.cyclomatic_complexity,
                status=IndexStatus.COMPLETED.value,
            )
            db.add(idx_file)
            await db.commit()
            await db.refresh(idx_file)


            # Persist Symbols
            symbol_map: dict[str, uuid.UUID] = {}
            for sym in parsed.symbols:
                db_sym = CodeSymbol(
                    repository_id=repo_id,
                    indexed_file_id=idx_file.id,
                    name=sym.name,
                    fqn=sym.fqn,
                    namespace=sym.namespace,
                    package=sym.package,
                    symbol_type=sym.symbol_type,
                    visibility=sym.visibility,
                    modifiers=sym.modifiers,
                    return_type=sym.return_type,
                    parameter_count=sym.parameter_count,
                    signature=sym.signature,
                    docstring=sym.docstring,
                    start_line=sym.start_line,
                    end_line=sym.end_line,
                    start_column=sym.start_column,
                    end_column=sym.end_column,
                )
                db.add(db_sym)
                await db.flush()
                symbol_map[sym.name] = db_sym.id

                if sym.symbol_type == "class":
                    total_classes += 1
                elif sym.symbol_type == "function":
                    total_functions += 1
                elif sym.symbol_type == "method":
                    total_methods += 1

            # Persist Chunks (NO RAW CONTENT)
            for chk in parsed.chunks:
                parent_id = symbol_map.get(chk.parent_symbol_name) if chk.parent_symbol_name else None
                db_chk = CodeChunk(
                    repository_id=repo_id,
                    indexed_file_id=idx_file.id,
                    parent_symbol_id=parent_id,
                    branch=repo.default_branch or "main",
                    chunk_hash=chk.chunk_hash,
                    chunk_type=chk.chunk_type,
                    language=parsed.language,
                    start_line=chk.start_line,
                    end_line=chk.end_line,
                    token_estimate=chk.token_estimate,
                )
                db.add(db_chk)

            # Persist Import Graphs & Dependencies
            for dep in parsed.dependencies:
                db_imp = ImportGraph(
                    repository_id=repo_id,
                    source_file_path=rel_path,
                    target_module=dep.target_module,
                    imported_symbols=dep.imported_symbols,
                )
                db.add(db_imp)

                db_dep = DependencyGraph(
                    repository_id=repo_id,
                    source_path=rel_path,
                    target_path=dep.target_module,
                    dependency_type=dep.dependency_type,
                )
                db.add(db_dep)

            # Update accumulator counters
            total_lines += parsed.line_count
            total_symbols += parsed.symbol_count
            total_chunks += parsed.chunk_count
            total_complexity += parsed.cyclomatic_complexity
            if parsed.cyclomatic_complexity > max_complexity:
                max_complexity = parsed.cyclomatic_complexity

            todo_count += parsed.todo_count
            fixme_count += parsed.fixme_count
            docstring_count += parsed.docstring_count

            # Update Language Stats accumulator
            if parsed.language not in lang_stats:
                lang_stats[parsed.language] = {"files": 0, "lines": 0, "bytes": 0}
            lang_stats[parsed.language]["files"] += 1
            lang_stats[parsed.language]["lines"] += parsed.line_count
            lang_stats[parsed.language]["bytes"] += file_size

            processed_count += 1
            checkpoint.last_processed_file = rel_path
            checkpoint.processed_files_count = processed_count
            db.add(checkpoint)

            job.processed_files = processed_count
            job.progress_pct = (processed_count / max(1, total_files_count)) * 100.0
            db.add(job)

            await db.commit()

        # Update RepositoryIndex
        repo_index.status = IndexStatus.COMPLETED.value
        repo_index.total_files = total_files_count
        repo_index.total_symbols = total_symbols
        repo_index.total_chunks = total_chunks
        repo_index.total_lines = total_lines
        repo_index.indexed_at = datetime.now(timezone.utc)
        db.add(repo_index)

        # Persist Language Statistics
        await db.execute(
            delete(LanguageStatistic).filter(LanguageStatistic.repository_id == repo_id)
        )
        total_bytes_all = sum(s["bytes"] for s in lang_stats.values()) or 1
        for lang, stats in lang_stats.items():
            pct = (stats["bytes"] / total_bytes_all) * 100.0
            db_ls = LanguageStatistic(
                repository_id=repo_id,
                language=lang,
                file_count=stats["files"],
                line_count=stats["lines"],
                bytes=stats["bytes"],
                percentage=round(pct, 2),
            )
            db.add(db_ls)

        # Persist RepositoryMetrics
        avg_comp = (total_complexity / max(1, total_files_count))
        maint_idx = max(0.0, min(100.0, 100.0 - (avg_comp * 3.0)))
        doc_cov = (docstring_count / max(1, total_symbols)) * 100.0

        metric_query = select(RepositoryMetric).filter(RepositoryMetric.repository_id == repo_id)
        m_res = await db.execute(metric_query)
        metric = m_res.scalars().first()
        if not metric:
            metric = RepositoryMetric(repository_id=repo_id)

        metric.total_files = total_files_count
        metric.total_lines = total_lines
        metric.total_symbols = total_symbols
        metric.total_chunks = total_chunks
        metric.average_complexity = round(avg_comp, 2)
        metric.maintainability_index = round(maint_idx, 2)
        metric.largest_file_path = largest_file_path
        metric.largest_file_bytes = largest_file_bytes
        metric.deepest_directory_depth = deepest_dir_depth
        metric.total_classes = total_classes
        metric.total_functions = total_functions
        metric.total_methods = total_methods
        metric.todo_count = todo_count
        metric.fixme_count = fixme_count
        metric.documentation_coverage_pct = round(doc_cov, 2)
        metric.language_distribution = {l: s["bytes"] for l, s in lang_stats.items()}
        db.add(metric)

        # Update Job completion
        job.status = IndexStatus.COMPLETED.value
        job.progress_pct = 100.0
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)

        # Mark repo indexing ready
        repo.indexing_ready = True
        repo.sync_status = SyncStatus.SYNCED.value
        db.add(repo)

        await db.commit()

        elapsed = time.perf_counter() - start_time
        logger.info(
            "Repository indexing pipeline complete",
            extra={
                "repo_id": str(repo_id),
                "total_files": total_files_count,
                "total_symbols": total_symbols,
                "total_chunks": total_chunks,
                "elapsed_sec": round(elapsed, 2),
            },
        )
        return repo_index


indexing_engine = IndexingEngine()
