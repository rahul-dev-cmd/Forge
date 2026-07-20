"""Python Language Parser using AST."""

from __future__ import annotations

import ast
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


class PythonParser(BaseParser):
    def parse(self, file_path: str, content: str) -> ParsedFileResult:
        lines = content.splitlines()
        line_count = len(lines)

        todo_count = len(re.findall(r"#\s*TODO\b", content, re.IGNORECASE))
        fixme_count = len(re.findall(r"#\s*FIXME\b", content, re.IGNORECASE))

        symbols: list[ExtractedSymbol] = []
        dependencies: list[ExtractedDependency] = []
        chunks: list[ExtractedChunk] = []
        docstring_count = 0
        complexity = 1

        try:
            tree = ast.parse(content, filename=file_path)
        except Exception:
            # Fallback if AST parsing fails
            return ParsedFileResult(
                file_path=file_path,
                language="python",
                line_count=line_count,
                symbol_count=0,
                chunk_count=1,
                cyclomatic_complexity=1,
                todo_count=todo_count,
                fixme_count=fixme_count,
                chunks=[
                    ExtractedChunk(
                        chunk_type="file",
                        start_line=1,
                        end_line=max(1, line_count),
                        token_estimate=calculate_token_estimate(lines, 1, line_count),
                        chunk_hash=compute_chunk_hash(file_path, 1, line_count),
                    )
                ],
            )

        module_name = file_path.replace("/", ".").removesuffix(".py")

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1

            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(
                        ExtractedDependency(
                            target_module=alias.name,
                            dependency_type="import",
                            imported_symbols=[alias.asname or alias.name],
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                syms = [alias.name for alias in node.names]
                dependencies.append(
                    ExtractedDependency(
                        target_module=mod,
                        dependency_type="import",
                        imported_symbols=syms,
                    )
                )

            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                if doc:
                    docstring_count += 1

                fqn = f"{module_name}.{node.name}"
                start_l = node.lineno
                end_l = getattr(node, "end_lineno", start_l)

                symbols.append(
                    ExtractedSymbol(
                        name=node.name,
                        fqn=fqn,
                        symbol_type="class",
                        start_line=start_l,
                        end_line=end_l,
                        start_column=node.col_offset,
                        visibility="private" if node.name.startswith("_") else "public",
                        docstring=doc,
                        signature=f"class {node.name}",
                    )
                )

                chunks.append(
                    ExtractedChunk(
                        chunk_type="class",
                        start_line=start_l,
                        end_line=end_l,
                        token_estimate=calculate_token_estimate(lines, start_l, end_l),
                        chunk_hash=compute_chunk_hash(file_path, start_l, end_l),
                        parent_symbol_name=node.name,
                    )
                )

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    docstring_count += 1

                is_async = isinstance(node, ast.AsyncFunctionDef)
                modifiers = ["async"] if is_async else []

                start_l = node.lineno
                end_l = getattr(node, "end_lineno", start_l)
                param_count = len(node.args.args)

                # Determine if method or top-level function
                is_method = False
                parent_name = None
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef) and node in parent.body:
                        is_method = True
                        parent_name = parent.name
                        break

                sym_type = "method" if is_method else "function"
                fqn = f"{module_name}.{parent_name}.{node.name}" if parent_name else f"{module_name}.{node.name}"

                symbols.append(
                    ExtractedSymbol(
                        name=node.name,
                        fqn=fqn,
                        symbol_type=sym_type,
                        start_line=start_l,
                        end_line=end_l,
                        start_column=node.col_offset,
                        visibility="private" if node.name.startswith("_") else "public",
                        modifiers=modifiers,
                        parameter_count=param_count,
                        docstring=doc,
                        signature=f"def {node.name}(...)",
                        parent_name=parent_name,
                    )
                )

                chunks.append(
                    ExtractedChunk(
                        chunk_type=sym_type,
                        start_line=start_l,
                        end_line=end_l,
                        token_estimate=calculate_token_estimate(lines, start_l, end_l),
                        chunk_hash=compute_chunk_hash(file_path, start_l, end_l),
                        parent_symbol_name=node.name,
                    )
                )

        if not chunks:
            chunks.append(
                ExtractedChunk(
                    chunk_type="file",
                    start_line=1,
                    end_line=max(1, line_count),
                    token_estimate=calculate_token_estimate(lines, 1, line_count),
                    chunk_hash=compute_chunk_hash(file_path, 1, line_count),
                )
            )

        return ParsedFileResult(
            file_path=file_path,
            language="python",
            line_count=line_count,
            symbol_count=len(symbols),
            chunk_count=len(chunks),
            cyclomatic_complexity=complexity,
            symbols=symbols,
            dependencies=dependencies,
            chunks=chunks,
            todo_count=todo_count,
            fixme_count=fixme_count,
            docstring_count=docstring_count,
        )
