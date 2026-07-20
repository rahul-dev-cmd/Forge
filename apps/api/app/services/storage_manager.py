"""Repository Storage Manager — Secure local git storage management."""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from app.config.settings import settings
from app.utils.logger import logger


class StorageSecurityError(Exception):
    """Raised when path traversal or security limits are violated."""


class RepositoryStorageManager:
    """
    Manages local git repository clones outside the web root.
    Handles cloning, pulling, path sanitization, storage quotas, and cleanup.
    """

    def __init__(self, base_storage_path: str | Path | None = None):
        if base_storage_path:
            self.base_path = Path(base_storage_path).resolve()
        else:
            # Place storage outside web root inside workspace/app storage directory
            self.base_path = Path(os.getcwd()).resolve() / "storage" / "repositories"
        
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Quotas and Security Limits
        self.max_repo_size_bytes = 500 * 1024 * 1024  # 500 MB limit
        self.max_file_size_bytes = 2 * 1024 * 1024    # 2 MB per file limit

        # Directories and paths ignored during indexing/scanning
        self.ignored_dirs = frozenset(
            {
                ".git",
                "node_modules",
                "vendor",
                "dist",
                "build",
                ".next",
                ".venv",
                "venv",
                "env",
                "__pycache__",
                "target",
                ".idea",
                ".vscode",
                "coverage",
                ".turbo",
            }
        )

        # Binary file extensions ignored during symbol parsing
        self.binary_extensions = frozenset(
            {
                ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".pdf",
                ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so",
                ".dylib", ".class", ".jar", ".pyc", ".pyo", ".db", ".sqlite",
                ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4", ".wav", ".avi",
                ".iso", ".dmg", ".bin", ".wasm", ".icns", ".map",
            }
        )

        # Generated file suffixes and names to exclude
        self.generated_suffixes = frozenset(
            {
                ".min.js", ".min.css", ".bundle.js", ".min.map", ".js.map", ".css.map",
            }
        )
        self.generated_filenames = frozenset(
            {
                "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "cargo.lock", "poetry.lock",
            }
        )


    def get_repo_dir(self, repo_id: uuid.UUID) -> Path:
        """
        Get resolved directory path for a repository.
        """
        repo_dir = (self.base_path / str(repo_id)).resolve()
        base_resolved = self.base_path.resolve()
        try:
            repo_dir.relative_to(base_resolved)
        except ValueError:
            raise StorageSecurityError("Path traversal attack detected")
        return repo_dir


    def sanitize_relative_path(self, repo_id: uuid.UUID, relative_path: str) -> Path:
        """
        Sanitize and validate a relative file path inside the repository root.
        Prevents directory traversal attacks.
        """
        repo_dir = self.get_repo_dir(repo_id)
        target_path = (repo_dir / relative_path).resolve()
        try:
            target_path.relative_to(repo_dir)
        except ValueError:
            raise StorageSecurityError(f"Directory traversal prevented: '{relative_path}' escapes repository root")
        return target_path

    def to_relative_path(self, repo_id: uuid.UUID, absolute_path: Path) -> str:
        """
        Convert an absolute filesystem path to a clean relative path for API responses.
        Never exposes local server paths.
        """
        repo_dir = self.get_repo_dir(repo_id)
        resolved = absolute_path.resolve()
        relative = resolved.relative_to(repo_dir)
        return str(relative).replace("\\", "/")

    def clone_repository(
        self, repo_id: uuid.UUID, clone_url: str, token: str | None = None
    ) -> Path:
        """
        Clone a git repository to local storage.
        """
        repo_dir = self.get_repo_dir(repo_id)
        if repo_dir.exists():
            logger.info("Repository storage exists; performing pull instead of clone", extra={"repo_id": str(repo_id)})
            return self.pull_repository(repo_id)

        # Inject auth token into HTTPS clone URL if provided
        auth_clone_url = clone_url
        if token and clone_url.startswith("https://"):
            auth_clone_url = clone_url.replace("https://", f"https://x-access-token:{token}@")

        logger.info("Cloning repository", extra={"repo_id": str(repo_id)})
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", auth_clone_url, str(repo_dir)],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.CalledProcessError as e:
            logger.error("Git clone failed", extra={"repo_id": str(repo_id), "stderr": e.stderr})
            raise RuntimeError(f"Git clone failed: {e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Git clone operation timed out after 300 seconds") from e

        # Enforce storage quota
        self._enforce_quota(repo_id)
        return repo_dir

    def pull_repository(self, repo_id: uuid.UUID) -> Path:
        """
        Pull latest changes for an existing clone.
        """
        repo_dir = self.get_repo_dir(repo_id)
        if not repo_dir.exists():
            raise FileNotFoundError(f"Repository storage for {repo_id} does not exist")

        logger.info("Pulling latest repository changes", extra={"repo_id": str(repo_id)})
        try:
            subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=str(repo_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.CalledProcessError as e:
            logger.warning("Git pull failed; attempting fetch & reset", extra={"repo_id": str(repo_id), "stderr": e.stderr})
            subprocess.run(
                ["git", "fetch", "--all"],
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                timeout=180,
            )

        self._enforce_quota(repo_id)
        return repo_dir

    def get_current_commit_sha(self, repo_id: uuid.UUID) -> str:
        """
        Get HEAD commit SHA of local clone.
        """
        repo_dir = self.get_repo_dir(repo_id)
        if not repo_dir.exists():
            return "HEAD"
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
        )
        return res.stdout.strip() or "HEAD"

    def delete_repository_storage(self, repo_id: uuid.UUID) -> bool:
        """
        Purge local repository disk storage.
        """
        repo_dir = self.get_repo_dir(repo_id)
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
            logger.info("Deleted repository storage", extra={"repo_id": str(repo_id)})
            return True
        return False

    def list_indexable_files(self, repo_id: uuid.UUID) -> list[tuple[str, Path]]:
        """
        Walk repository directory and return list of (clean_relative_path, absolute_path) tuples,
        skipping ignored directories and binary files.
        """
        repo_dir = self.get_repo_dir(repo_id)
        if not repo_dir.exists():
            return []

        indexable: list[tuple[str, Path]] = []

        for root, dirs, files in os.walk(repo_dir):
            # Prune ignored directory names in-place
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith(".")]

            for file_name in files:
                if file_name.startswith("."):
                    continue
                
                fn_lower = file_name.lower()
                if fn_lower in self.generated_filenames:
                    continue

                if any(fn_lower.endswith(suf) for suf in self.generated_suffixes):
                    continue

                abs_file = Path(root) / file_name
                ext = abs_file.suffix.lower()
                if ext in self.binary_extensions:
                    continue

                # Enforce single file size limit
                try:
                    if abs_file.stat().st_size > self.max_file_size_bytes:
                        continue
                except OSError:
                    continue

                rel_path = self.to_relative_path(repo_id, abs_file)
                indexable.append((rel_path, abs_file))

        return indexable


    def _enforce_quota(self, repo_id: uuid.UUID) -> None:
        """
        Calculate repository size on disk and verify against max quota limit.
        """
        repo_dir = self.get_repo_dir(repo_id)
        total_bytes = 0
        for root, _, files in os.walk(repo_dir):
            for f in files:
                fp = Path(root) / f
                try:
                    total_bytes += fp.stat().st_size
                except OSError:
                    pass

        if total_bytes > self.max_repo_size_bytes:
            self.delete_repository_storage(repo_id)
            raise StorageSecurityError(
                f"Repository size ({total_bytes / (1024*1024):.1f} MB) exceeds maximum quota limit ({self.max_repo_size_bytes / (1024*1024):.0f} MB)"
            )


storage_manager = RepositoryStorageManager()
