"""Citation Manager — Extracts and formats citations from ContextPackage."""

from __future__ import annotations

from typing import Any


class CitationManager:
    """Formats citations from retrieved ContextPackage data."""

    def extract_citations(self, context_pkg: dict[str, Any] | None) -> list[dict[str, Any]]:
        if not context_pkg:
            return []

        citations = []
        raw_citations = context_pkg.get("citations", [])
        for c in raw_citations:
            citations.append({
                "file_path": c.get("file_path", ""),
                "start_line": c.get("start_line", 1),
                "end_line": c.get("end_line", 100),
                "confidence": c.get("score", 0.9),
            })
        return citations


citation_manager = CitationManager()
