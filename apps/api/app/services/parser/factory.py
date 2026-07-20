"""Parser Factory for mapping language names to specific language parser implementations."""

from __future__ import annotations

from app.services.parser.base import BaseParser
from app.services.parser.languages.generic_parser import GenericLanguageParser
from app.services.parser.languages.python_parser import PythonParser


class ParserFactory:
    """
    Factory creating parser instances for Python, TypeScript, JavaScript, Java,
    C, C++, Go, Rust, Markdown, JSON, YAML, SQL.
    """

    def __init__(self):
        self._python_parser = PythonParser()
        self._cache: dict[str, BaseParser] = {
            "python": self._python_parser,
        }

    def get_parser(self, language: str) -> BaseParser:
        lang_key = language.lower()
        if lang_key in self._cache:
            return self._cache[lang_key]

        # Use GenericLanguageParser for TS, JS, Java, C, C++, Go, Rust, Markdown, JSON, YAML, SQL
        parser = GenericLanguageParser(lang_key)
        self._cache[lang_key] = parser
        return parser


parser_factory = ParserFactory()
