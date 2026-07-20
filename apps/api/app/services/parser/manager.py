"""ParserManager — Primary entry point for code parsing and AST symbol extraction."""

from __future__ import annotations

from app.services.parser.base import ParsedFileResult
from app.services.parser.factory import parser_factory
from app.services.parser.language_detector import language_detector
from app.utils.logger import logger


class ParserManager:
    """
    Orchestrates Language Detection -> Parser Factory -> Language Parser execution.
    """

    def parse_file(self, file_path: str, content: str) -> ParsedFileResult:
        language = language_detector.detect_language(file_path)
        parser = parser_factory.get_parser(language)

        try:
            return parser.parse(file_path, content)
        except Exception as e:
            logger.exception("Parser error", extra={"file_path": file_path, "language": language})
            lines = content.splitlines()
            line_count = len(lines)
            return ParsedFileResult(
                file_path=file_path,
                language=language,
                line_count=line_count,
                symbol_count=0,
                chunk_count=1,
                cyclomatic_complexity=1,
            )


parser_manager = ParserManager()
