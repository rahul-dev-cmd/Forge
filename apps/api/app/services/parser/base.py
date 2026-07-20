"""Base Parser Interface and Data Structures for Code Intelligence Parsing."""

from __future__ import annotations

import abc
import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedSymbol:
    name: str
    fqn: str
    symbol_type: str  # class, function, method, interface, enum, variable, constant
    start_line: int
    end_line: int
    start_column: int = 0
    end_column: int = 0
    namespace: str | None = None
    package: str | None = None
    visibility: str = "public"  # public, private, protected
    modifiers: list[str] = field(default_factory=list)  # async, static, final
    return_type: str | None = None
    parameter_count: int = 0
    signature: str | None = None
    docstring: str | None = None
    parent_name: str | None = None


@dataclass
class ExtractedReference:
    caller_fqn: str
    callee_fqn: str
    reference_type: str  # call, instantiation, inheritance, import, usage
    line_number: int


@dataclass
class ExtractedDependency:
    target_module: str
    dependency_type: str  # import, export, package
    imported_symbols: list[str] = field(default_factory=list)


@dataclass
class ExtractedChunk:
    chunk_type: str  # function, class, module, file, block
    start_line: int
    end_line: int
    token_estimate: int
    chunk_hash: str
    parent_symbol_name: str | None = None


@dataclass
class ParsedFileResult:
    file_path: str
    language: str
    line_count: int
    symbol_count: int
    chunk_count: int
    cyclomatic_complexity: int
    symbols: list[ExtractedSymbol] = field(default_factory=list)
    references: list[ExtractedReference] = field(default_factory=list)
    dependencies: list[ExtractedDependency] = field(default_factory=list)
    chunks: list[ExtractedChunk] = field(default_factory=list)
    todo_count: int = 0
    fixme_count: int = 0
    docstring_count: int = 0


def calculate_token_estimate(lines: list[str], start_line: int, end_line: int) -> int:
    """Approximate token count (characters / 4)."""
    text = "\n".join(lines[start_line - 1 : end_line])
    return max(1, len(text) // 4)


def compute_chunk_hash(file_path: str, start_line: int, end_line: int) -> str:
    """Generate SHA256 chunk hash identifier."""
    raw = f"{file_path}:{start_line}:{end_line}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class BaseParser(abc.ABC):
    """
    Abstract base class for all language-specific code parsers.
    """

    @abc.abstractmethod
    def parse(self, file_path: str, content: str) -> ParsedFileResult:
        """
        Parse source file content into structured AST symbols, dependencies, and chunks.
        """
        pass
