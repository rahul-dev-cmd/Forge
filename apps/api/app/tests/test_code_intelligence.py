"""Tests for Milestone 7 — Code Intelligence & Indexing System."""

import pytest
from pathlib import Path
from app.services.parser.language_detector import language_detector
from app.services.parser.manager import parser_manager
from app.services.storage_manager import storage_manager, StorageSecurityError
import uuid


def test_language_detection():
    assert language_detector.detect_language("main.py") == "python"
    assert language_detector.detect_language("app/index.ts") == "typescript"
    assert language_detector.detect_language("components/Button.tsx") == "typescript"
    assert language_detector.detect_language("server.js") == "javascript"
    assert language_detector.detect_language("Main.java") == "java"
    assert language_detector.detect_language("main.cpp") == "cpp"
    assert language_detector.detect_language("main.go") == "go"
    assert language_detector.detect_language("main.rs") == "rust"
    assert language_detector.detect_language("README.md") == "markdown"
    assert language_detector.detect_language("schema.sql") == "sql"


def test_python_ast_parser():
    code = '''
def add(a: int, b: int) -> int:
    """Adds two integers."""
    # TODO: add overflow validation
    return a + b

class Calculator:
    """A simple calculator."""
    def multiply(self, x, y):
        return x * y
'''
    parsed = parser_manager.parse_file("calculator.py", code)
    assert parsed.language == "python"
    assert parsed.line_count > 0
    assert parsed.symbol_count >= 3  # add, Calculator, multiply
    assert parsed.todo_count == 1
    assert parsed.docstring_count == 2
    assert len(parsed.chunks) >= 2


def test_generic_parser():
    js_code = '''
import { useState } from 'react';

// TODO: refactor component
export function Counter() {
    const [count, setCount] = useState(0);
    return count;
}
'''
    parsed = parser_manager.parse_file("Counter.js", js_code)
    assert parsed.language == "javascript"
    assert parsed.symbol_count >= 1
    assert len(parsed.dependencies) == 1
    assert parsed.dependencies[0].target_module == "react"


def test_storage_path_sanitization():
    repo_id = uuid.uuid4()
    # Path inside repo
    safe = storage_manager.sanitize_relative_path(repo_id, "src/index.py")
    assert str(safe).endswith("src\\index.py") or str(safe).endswith("src/index.py")

    # Path escaping repo root
    with pytest.raises(StorageSecurityError):
        storage_manager.sanitize_relative_path(repo_id, "../../etc/passwd")
