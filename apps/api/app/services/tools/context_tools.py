"""Context Tools — 10 Tools encapsulating ContextPackage retrieval for AI Agents."""

from __future__ import annotations

import uuid
from typing import Any

from app.services.context_builder import context_builder
from app.services.retrieval_engine import retrieval_engine
from app.services.storage_manager import storage_manager
from app.services.tools.base import InternalTool, ToolResult


class RepositorySearchTool(InternalTool):
    name = "repository_search"
    description = "Searches code snippets using hybrid vector and keyword matching."
    permissions = ("code.search", "repository.read")

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        workspace_id = context["workspace_id"]
        repo_id = context["repository_id"]
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 5)

        results = await retrieval_engine.search(db, workspace_id, repo_id, query, top_k=top_k)
        serialized = [
            {"file_path": r.file_path, "lines": f"{r.start_line}-{r.end_line}", "score": r.final_score, "content": r.content[:300]}
            for r in results
        ]
        return ToolResult(success=True, output=serialized)


class SemanticSearchTool(InternalTool):
    name = "semantic_search"
    description = "Performs vector similarity search against the codebase index."
    permissions = ("code.search", "repository.read")

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        return await RepositorySearchTool().run(kwargs, context)


class ContextRetrievalTool(InternalTool):
    name = "context_retrieval"
    description = "Assembles a comprehensive RAG ContextPackage with symbols, imports, and citations."
    permissions = ("code.search", "repository.read")

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        workspace_id = context["workspace_id"]
        repo_id = context["repository_id"]
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 5)

        pkg = await context_builder.build_context_package(db, workspace_id, repo_id, query, top_k=top_k)
        return ToolResult(success=True, output=pkg)


class FileReaderTool(InternalTool):
    name = "file_reader"
    description = "Reads specific source file line ranges from local git clone."
    permissions = ("repository.read",)

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        repo_id = context["repository_id"]
        rel_path = kwargs.get("file_path", "")
        start_line = kwargs.get("start_line", 1)
        end_line = kwargs.get("end_line", 100)

        try:
            repo_dir = storage_manager.get_repo_dir(repo_id)
            abs_path = repo_dir / rel_path
            lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
            snippet = "\n".join(lines[start_line - 1 : end_line])
            return ToolResult(success=True, output={"file_path": rel_path, "content": snippet})
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"File read error: {e}")


class SymbolLookupTool(InternalTool):
    name = "symbol_lookup"
    description = "Looks up extracted AST symbols (classes, functions, methods) by name."
    permissions = ("code.search", "repository.read")

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        repo_id = context["repository_id"]
        query = kwargs.get("name", "")

        from sqlalchemy import select
        from app.models.code_intelligence import CodeSymbol
        res = await db.execute(
            select(CodeSymbol).filter(
                CodeSymbol.repository_id == repo_id, CodeSymbol.name.ilike(f"%{query}%")
            ).limit(10)
        )
        symbols = res.scalars().all()
        serialized = [
            {"name": s.name, "fqn": s.fqn, "type": s.symbol_type, "lines": f"{s.start_line}-{s.end_line}"}
            for s in symbols
        ]
        return ToolResult(success=True, output=serialized)


class DependencyLookupTool(InternalTool):
    name = "dependency_lookup"
    description = "Queries module import and file dependency graphs."
    permissions = ("code.search", "repository.read")

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        repo_id = context["repository_id"]
        file_path = kwargs.get("file_path", "")

        from sqlalchemy import select
        from app.models.code_intelligence import ImportGraph, DependencyGraph

        imp_res = await db.execute(
            select(ImportGraph).filter(ImportGraph.repository_id == repo_id, ImportGraph.source_file_path == file_path)
        )
        imports = [i.target_module for i in imp_res.scalars().all()]
        return ToolResult(success=True, output={"file_path": file_path, "imports": imports})


class MetricsTool(InternalTool):
    name = "metrics_tool"
    description = "Fetches repository maintainability index and complexity metrics."
    permissions = ("repository.read",)

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        repo_id = context["repository_id"]

        from sqlalchemy import select
        from app.models.code_intelligence import RepositoryMetric
        res = await db.execute(select(RepositoryMetric).filter(RepositoryMetric.repository_id == repo_id))
        m = res.scalars().first()
        if not m:
            return ToolResult(success=False, output=None, error="No metrics found")
        return ToolResult(
            success=True,
            output={
                "total_files": m.total_files,
                "total_lines": m.total_lines,
                "maintainability_index": m.maintainability_index,
                "average_complexity": m.average_complexity,
                "todo_count": m.todo_count,
            },
        )


class GitHistoryTool(InternalTool):
    name = "git_history"
    description = "Queries git commits and branch metadata."
    permissions = ("repository.read",)

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        sha = storage_manager.get_current_commit_sha(context["repository_id"])
        return ToolResult(success=True, output={"head_commit": sha})


class DocumentationTool(InternalTool):
    name = "documentation_tool"
    description = "Extracts docstrings, API descriptions, and README documentation."
    permissions = ("repository.read",)

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        repo_id = context["repository_id"]
        repo_dir = storage_manager.get_repo_dir(repo_id)
        readme = ""
        for name in ("README.md", "readme.md"):
            p = repo_dir / name
            if p.exists():
                readme = p.read_text(encoding="utf-8", errors="replace")[:1000]
                break
        return ToolResult(success=True, output={"readme_snippet": readme})


class RepositorySummaryTool(InternalTool):
    name = "repository_summary"
    description = "Generates high-level repository summary and language breakdown."
    permissions = ("repository.read",)

    async def run(self, kwargs: dict[str, Any], context: dict[str, Any]) -> ToolResult:
        db = context["db"]
        repo_id = context["repository_id"]

        from sqlalchemy import select
        from app.models.code_intelligence import LanguageStatistic
        res = await db.execute(select(LanguageStatistic).filter(LanguageStatistic.repository_id == repo_id))
        stats = [
            {"language": s.language, "percentage": s.percentage, "file_count": s.file_count}
            for s in res.scalars().all()
        ]
        return ToolResult(success=True, output={"languages": stats})
