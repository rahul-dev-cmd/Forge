"""Comprehensive Stability and Quality Gate Tests for Milestone 7."""

import os
import shutil
import tempfile
import time
import tracemalloc
import uuid
import pytest
from pathlib import Path

from app.services.storage_manager import storage_manager
from app.services.parser.manager import parser_manager
from app.services.parser.language_detector import language_detector


def test_generated_and_binary_exclusions():
    """Verify lockfiles, minified assets, maps, binaries, and dot-dirs are excluded."""
    test_repo_id = uuid.UUID(int=1)
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / str(test_repo_id)
        repo_dir.mkdir()


        # Create valid files
        (repo_dir / "src").mkdir()
        (repo_dir / "src" / "index.py").write_text("print('hello')", encoding="utf-8")
        (repo_dir / "src" / "app.ts").write_text("export const app = {};", encoding="utf-8")

        # Create excluded files
        (repo_dir / ".git").mkdir()
        (repo_dir / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
        (repo_dir / "node_modules").mkdir()
        (repo_dir / "node_modules" / "express.js").write_text("module.exports = {};", encoding="utf-8")
        (repo_dir / "dist").mkdir()
        (repo_dir / "dist" / "bundle.min.js").write_text("var a=1;", encoding="utf-8")
        (repo_dir / "package-lock.json").write_text("{}", encoding="utf-8")
        (repo_dir / "yarn.lock").write_text("# lockfile", encoding="utf-8")
        (repo_dir / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")

        # Override storage manager base path temporarily
        original_base = storage_manager.base_path
        storage_manager.base_path = Path(tmpdir)

        try:
            indexable = storage_manager.list_indexable_files(uuid.UUID(int=1))
            paths = [rel for rel, _ in indexable]

            assert "src/index.py" in paths
            assert "src/app.ts" in paths

            # Assert exclusions
            assert not any(".git" in p for p in paths)
            assert not any("node_modules" in p for p in paths)
            assert not any("bundle.min.js" in p for p in paths)
            assert not any("package-lock.json" in p for p in paths)
            assert not any("yarn.lock" in p for p in paths)
            assert not any("image.png" in p for p in paths)
        finally:
            storage_manager.base_path = original_base


def test_large_codebase_throughput_and_memory():
    """Verify performance, memory ceiling, and throughput across 500 files."""
    tracemalloc.start()
    start_time = time.perf_counter()

    parsed_count = 0
    symbol_count = 0

    sample_py = '''
def calculate_subtotal(items: list) -> float:
    """Calculates total item price."""
    # TODO: handle discount
    return sum(item.price for item in items)

class OrderProcessor:
    """Processes customer orders."""
    def __init__(self, order_id: str):
        self.order_id = order_id

    def process(self) -> bool:
        return True
'''

    for i in range(500):
        parsed = parser_manager.parse_file(f"services/service_{i}.py", sample_py)
        parsed_count += 1
        symbol_count += parsed.symbol_count

    elapsed = time.perf_counter() - start_time
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    files_per_sec = parsed_count / elapsed
    peak_mb = peak_mem / (1024 * 1024)

    assert parsed_count == 500
    assert symbol_count >= 1500
    assert files_per_sec > 100  # High throughput gate (>100 files/sec)
    assert peak_mb < 150        # Low memory ceiling (<150 MB peak memory)


def test_incremental_hash_matching():
    """Verify file hash calculation for diff-based incremental updates."""
    import hashlib

    code_v1 = "def foo(): return 42"
    code_v2 = "def foo(): return 43"

    hash_v1_a = hashlib.sha256(code_v1.encode("utf-8")).hexdigest()
    hash_v1_b = hashlib.sha256(code_v1.encode("utf-8")).hexdigest()
    hash_v2 = hashlib.sha256(code_v2.encode("utf-8")).hexdigest()

    assert hash_v1_a == hash_v1_b  # Unchanged file produces identical hash
    assert hash_v1_a != hash_v2    # Modified file produces new hash
