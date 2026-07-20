"""Language Detector for mapping file paths to supported languages."""

from __future__ import annotations

from pathlib import Path


class LanguageDetector:
    """
    Detects programming language from file extensions or filenames.
    Supports Python, TypeScript, JavaScript, Java, C, C++, Go, Rust, Markdown, JSON, YAML, SQL.
    """

    EXTENSION_MAP: dict[str, str] = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".java": "java",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".md": "markdown",
        ".markdown": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sql": "sql",
    }

    FILENAME_MAP: dict[str, str] = {
        "dockerfile": "dockerfile",
        "makefile": "makefile",
        "cmakelists.txt": "cmake",
    }

    @classmethod
    def detect_language(cls, file_path: str) -> str:
        path = Path(file_path)
        name_lower = path.name.lower()
        if name_lower in cls.FILENAME_MAP:
            return cls.FILENAME_MAP[name_lower]
        
        ext = path.suffix.lower()
        return cls.EXTENSION_MAP.get(ext, "unknown")


language_detector = LanguageDetector()
