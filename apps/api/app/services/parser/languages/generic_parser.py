"""Generic / Regex-based Multi-Language Parser."""

from __future__ import annotations

import re

from app.services.parser.base import (
    BaseParser,
    ExtractedChunk,
    ExtractedDependency,
    ExtractedSymbol,
    ParsedFileResult,
    calculate_token_estimate,
    compute_chunk_hash,
)


class GenericLanguageParser(BaseParser):
    def __init__(self, language: str):
        self.language = language

    def parse(self, file_path: str, content: str) -> ParsedFileResult:
        lines = content.splitlines()
        line_count = len(lines)

        todo_count = len(re.findall(r"(//|#|/\*|--)\s*TODO\b", content, re.IGNORECASE))
        fixme_count = len(re.findall(r"(//|#|/\*|--)\s*FIXME\b", content, re.IGNORECASE))

        symbols: list[ExtractedSymbol] = []
        dependencies: list[ExtractedDependency] = []
        chunks: list[ExtractedChunk] = []
        complexity = 1

        module_name = file_path.replace("/", ".")

        # Language-specific patterns
        if self.language in ("typescript", "javascript"):
            # Imports
            for match in re.finditer(r"import\s+.*?from\s+['\"](.*?)['\"]", content):
                dependencies.append(
                    ExtractedDependency(target_module=match.group(1), dependency_type="import")
                )
            # Exports
            for match in re.finditer(r"export\s+(?:default\s+)?(?:class|function|const|let|var|interface|enum)\s+([A-Za-z0-9_]+)", content):
                pass
            # Classes / Interfaces / Enums
            for i, line in enumerate(lines, 1):
                m_class = re.search(r"\b(class|interface|enum)\s+([A-Za-z0-9_]+)", line)
                if m_class:
                    kind = m_class.group(1)
                    name = m_class.group(2)
                    symbols.append(
                        ExtractedSymbol(
                            name=name,
                            fqn=f"{module_name}.{name}",
                            symbol_type=kind,
                            start_line=i,
                            end_line=min(i + 20, line_count),
                            signature=line.strip(),
                        )
                    )
                    chunks.append(
                        ExtractedChunk(
                            chunk_type=kind,
                            start_line=i,
                            end_line=min(i + 20, line_count),
                            token_estimate=calculate_token_estimate(lines, i, min(i + 20, line_count)),
                            chunk_hash=compute_chunk_hash(file_path, i, min(i + 20, line_count)),
                            parent_symbol_name=name,
                        )
                    )
                m_func = re.search(r"\b(async\s+)?function\s+([A-Za-z0-9_]+)", line)
                if m_func:
                    name = m_func.group(2)
                    symbols.append(
                        ExtractedSymbol(
                            name=name,
                            fqn=f"{module_name}.{name}",
                            symbol_type="function",
                            start_line=i,
                            end_line=min(i + 15, line_count),
                            signature=line.strip(),
                        )
                    )

        elif self.language == "java":
            for match in re.finditer(r"import\s+([A-Za-z0-9_\.]+);", content):
                dependencies.append(ExtractedDependency(target_module=match.group(1), dependency_type="import"))
            for i, line in enumerate(lines, 1):
                m_class = re.search(r"\b(class|interface|enum)\s+([A-Za-z0-9_]+)", line)
                if m_class:
                    symbols.append(
                        ExtractedSymbol(
                            name=m_class.group(2),
                            fqn=f"{module_name}.{m_class.group(2)}",
                            symbol_type=m_class.group(1),
                            start_line=i,
                            end_line=min(i + 30, line_count),
                            signature=line.strip(),
                        )
                    )

        elif self.language in ("c", "cpp"):
            for match in re.finditer(r"#include\s+[<\"](.*?)[\">]", content):
                dependencies.append(ExtractedDependency(target_module=match.group(1), dependency_type="import"))
            for i, line in enumerate(lines, 1):
                m_struct = re.search(r"\b(struct|class|enum)\s+([A-Za-z0-9_]+)", line)
                if m_struct:
                    symbols.append(
                        ExtractedSymbol(
                            name=m_struct.group(2),
                            fqn=f"{module_name}.{m_struct.group(2)}",
                            symbol_type=m_struct.group(1),
                            start_line=i,
                            end_line=min(i + 25, line_count),
                            signature=line.strip(),
                        )
                    )

        elif self.language == "go":
            for match in re.finditer(r"import\s+(?:\(\s*([\s\S]*?)\s*\)|[\"'](.*?)[\"'])", content):
                dep = match.group(2) or match.group(1)
                if dep:
                    dependencies.append(ExtractedDependency(target_module=dep.strip(), dependency_type="import"))
            for i, line in enumerate(lines, 1):
                m_func = re.search(r"\bfunc\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)", line)
                if m_func:
                    symbols.append(
                        ExtractedSymbol(
                            name=m_func.group(1),
                            fqn=f"{module_name}.{m_func.group(1)}",
                            symbol_type="function",
                            start_line=i,
                            end_line=min(i + 20, line_count),
                            signature=line.strip(),
                        )
                    )

        elif self.language == "rust":
            for match in re.finditer(r"use\s+([A-Za-z0-9_:]+);", content):
                dependencies.append(ExtractedDependency(target_module=match.group(1), dependency_type="import"))
            for i, line in enumerate(lines, 1):
                m_struct = re.search(r"\b(struct|enum|trait|fn)\s+([A-Za-z0-9_]+)", line)
                if m_struct:
                    symbols.append(
                        ExtractedSymbol(
                            name=m_struct.group(2),
                            fqn=f"{module_name}.{m_struct.group(2)}",
                            symbol_type="function" if m_struct.group(1) == "fn" else m_struct.group(1),
                            start_line=i,
                            end_line=min(i + 20, line_count),
                            signature=line.strip(),
                        )
                    )

        elif self.language == "markdown":
            for i, line in enumerate(lines, 1):
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    symbols.append(
                        ExtractedSymbol(
                            name=title,
                            fqn=f"{file_path}#{title}",
                            symbol_type="constant",
                            start_line=i,
                            end_line=i,
                            signature=line.strip(),
                        )
                    )

        elif self.language == "sql":
            for match in re.finditer(r"CREATE\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)\s+([A-Za-z0-9_\.]+)", content, re.IGNORECASE):
                symbols.append(
                    ExtractedSymbol(
                        name=match.group(2),
                        fqn=f"{file_path}:{match.group(2)}",
                        symbol_type=match.group(1).lower(),
                        start_line=1,
                        end_line=line_count,
                        signature=match.group(0),
                    )
                )

        # Count cyclomatic complexity indicators ({}, if, for, while, switch, case)
        complexity += len(re.findall(r"\b(if|for|while|case|catch|&&|\|\|)\b", content))

        # Default chunk if none generated by symbols
        if not chunks:
            chunk_size = 50
            for start in range(1, line_count + 1, chunk_size):
                end = min(start + chunk_size - 1, line_count)
                chunks.append(
                    ExtractedChunk(
                        chunk_type="block",
                        start_line=start,
                        end_line=end,
                        token_estimate=calculate_token_estimate(lines, start, end),
                        chunk_hash=compute_chunk_hash(file_path, start, end),
                    )
                )

        return ParsedFileResult(
            file_path=file_path,
            language=self.language,
            line_count=line_count,
            symbol_count=len(symbols),
            chunk_count=len(chunks),
            cyclomatic_complexity=complexity,
            symbols=symbols,
            dependencies=dependencies,
            chunks=chunks,
            todo_count=todo_count,
            fixme_count=fixme_count,
        )
