"""Repository metadata sync engine — no cloning, no source code storage."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.integrations.github.app_auth import is_github_app_configured, GitHubAppAuthError
from app.integrations.github.client import GitHubClient, GitHubAPIError
from app.models.enums import JobStatus, SyncStatus, SyncJobType, ConnectionStatus, PullRequestStatus, IssueStatus
from app.models.git_metadata import (
    Branch,
    Commit,
    PullRequest,
    Issue,
    Contributor,
    RepositoryLanguage,
    RepositoryTopic,
)
from app.models.repository import Repository
from app.models.sync import RepositorySync
from app.models.activity import RepositoryActivity
from app.repositories.repository import repository_repository
from app.repositories.sync import repository_sync_repository
from app.repositories.git_metadata import (
    branch_repository,
    commit_repository,
    pull_request_repository,
    issue_repository,
    contributor_repository,
    language_repository,
    topic_repository,
)
from app.repositories.checkpoints import sync_checkpoint_repository
from app.services.rate_limit_service import rate_limit_service
from app.events.bus import event_bus, RepositorySynced, SyncCompleted
from app.utils.logger import logger


def _parse_gh_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _owner_repo(repository: Repository) -> tuple[str, str]:
    if repository.full_name and "/" in repository.full_name:
        owner, name = repository.full_name.split("/", 1)
        return owner, name
    if repository.owner:
        return repository.owner, repository.name
    raise ValueError("Repository owner/name not set")


class SyncEngine:
    async def create_sync_job(
        self,
        db: AsyncSession,
        *,
        repository_id: uuid.UUID | None,
        job_type: SyncJobType,
        triggered_by: uuid.UUID | None = None,
        installation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RepositorySync:
        job = RepositorySync(
            repository_id=repository_id,
            installation_id=installation_id,
            job_type=job_type.value,
            status=JobStatus.QUEUED.value,
            progress=0,
            triggered_by=triggered_by,
            metadata_json=json.dumps(metadata) if metadata else None,
            max_retries=settings.SYNC_MAX_RETRIES,
        )
        db.add(job)
        if repository_id:
            repo = await repository_repository.get(db, repository_id)
            if repo:
                repo.sync_status = SyncStatus.QUEUED.value
                repo.sync_error = None
                db.add(repo)
        await db.commit()
        await db.refresh(job)
        return job

    async def run_sync_job(self, db: AsyncSession, job_id: uuid.UUID) -> RepositorySync:
        job = await repository_sync_repository.get(db, job_id)
        if not job:
            raise ValueError(f"Sync job {job_id} not found")
        if job.status == JobStatus.CANCELLED.value:
            return job

        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.now(timezone.utc)
        job.progress = 5
        await db.commit()

        try:
            if not job.repository_id:
                raise ValueError("Sync job has no repository_id")

            repository = await repository_repository.get(db, job.repository_id)
            if not repository:
                raise ValueError("Repository not found")

            if not repository.installation_id:
                raise GitHubAppAuthError("Repository has no GitHub installation_id")

            if not is_github_app_configured():
                # Dev fallback: mark metadata as synced from existing fields
                await self._dev_noop_sync(db, repository, job)
                client = None
            else:
                client = GitHubClient(repository.installation_id)
                await self._sync_repository_metadata(db, repository, job, client)
                if client.last_rate_limit:
                    await rate_limit_service.record(
                        db,
                        installation_id=repository.installation_id,
                        remaining=client.last_rate_limit.get("remaining"),
                        limit=client.last_rate_limit.get("limit"),
                        reset_epoch=client.last_rate_limit.get("reset"),
                    )

            job.status = JobStatus.COMPLETED.value
            job.progress = 100
            job.finished_at = datetime.now(timezone.utc)
            job.error_message = None
            job.error_code = None

            checkpoint = await sync_checkpoint_repository.get_or_create(db, repository.id)
            last_commit_sha = checkpoint.last_commit_sha

            repository.sync_status = SyncStatus.SYNCED.value
            repository.sync_error = None
            repository.last_synced_at = datetime.now(timezone.utc)
            repository.connection_status = ConnectionStatus.CONNECTED.value
            repository.indexing_ready = True
            db.add(repository)

            if job.triggered_by:
                db.add(
                    RepositoryActivity(
                        repository_id=repository.id,
                        actor_id=job.triggered_by,
                        activity_type="repository_synced",
                        activity_metadata={"job_id": str(job.id), "job_type": job.job_type},
                    )
                )
            await db.commit()
            await db.refresh(job)
            logger.info(
                "Repository sync completed",
                extra={"job_id": str(job.id), "repository_id": str(repository.id)},
            )

            await event_bus.publish(
                RepositorySynced(
                    repository_id=str(repository.id),
                    sync_job_id=str(job.id),
                    job_type=job.job_type,
                    commits_synced=job.commits_synced,
                    indexing_ready=repository.indexing_ready,
                    supports_indexing=repository.supports_indexing,
                )
            )
            await event_bus.publish(
                SyncCompleted(
                    repository_id=str(repository.id),
                    sync_job_id=str(job.id),
                    job_type=job.job_type,
                    last_commit_sha=last_commit_sha,
                )
            )
            return job

        except (GitHubAPIError, GitHubAppAuthError, ValueError) as exc:
            return await self._fail_job(db, job, exc)
        except Exception as exc:
            logger.exception("Unexpected sync failure")
            return await self._fail_job(db, job, exc)

    async def _fail_job(
        self, db: AsyncSession, job: RepositorySync, exc: Exception
    ) -> RepositorySync:
        error_code = getattr(exc, "error_code", None) or type(exc).__name__
        message = str(exc)
        job.status = JobStatus.FAILED.value
        job.error_message = message
        job.error_code = error_code
        job.finished_at = datetime.now(timezone.utc)
        job.retry_count = (job.retry_count or 0) + 1

        if job.repository_id:
            repository = await repository_repository.get(db, job.repository_id)
            if repository:
                repository.sync_status = SyncStatus.FAILED.value
                repository.sync_error = message
                if error_code in {
                    "permission_revoked",
                    "installation_token_expired",
                }:
                    repository.connection_status = ConnectionStatus.EXPIRED.value
                elif error_code == "resource_not_found":
                    repository.connection_status = ConnectionStatus.ERROR.value
                db.add(repository)

        await db.commit()
        await db.refresh(job)
        logger.error(
            "Repository sync failed",
            extra={
                "job_id": str(job.id),
                "error_code": error_code,
                "error": message,
            },
        )
        return job

    async def _dev_noop_sync(
        self, db: AsyncSession, repository: Repository, job: RepositorySync
    ) -> None:
        """When GitHub App is not configured, keep local metadata consistent."""
        job.progress = 50
        repository.sync_status = SyncStatus.SYNCING.value
        db.add(repository)
        await db.commit()
        job.progress = 90
        await db.commit()

    async def _sync_repository_metadata(
        self,
        db: AsyncSession,
        repository: Repository,
        job: RepositorySync,
        client: GitHubClient,
    ) -> None:
        repository.sync_status = SyncStatus.SYNCING.value
        db.add(repository)
        await db.commit()

        owner, name = _owner_repo(repository)

        # 1. Repository metadata + stats
        remote = await client.get_repository(owner, name)
        await self._apply_repo_payload(db, repository, remote)
        job.progress = 15
        await db.commit()

        # 2. Languages
        languages = await client.get_languages(owner, name)
        await self._upsert_languages(db, repository.id, languages)
        job.progress = 25
        await db.commit()

        # 3. Topics
        topics_payload = await client.get_topics(owner, name)
        await self._upsert_topics(db, repository.id, topics_payload.get("names") or [])
        job.progress = 30
        await db.commit()

        # 4. README metadata (no content stored beyond path)
        readme = await client.get_readme_metadata(owner, name)
        repository.readme_exists = readme is not None
        repository.readme_path = (readme or {}).get("path")
        db.add(repository)
        job.progress = 35
        await db.commit()

        # 5. Branches
        branches = await client.list_branches(
            owner, name, per_page=settings.GITHUB_SYNC_BRANCH_LIMIT
        )
        default_branch = repository.default_branch
        for br in branches:
            await self._upsert_branch(db, repository.id, br, default_branch)
        job.branches_synced = len(branches)
        job.progress = 50
        await db.commit()

        # 6. Commits (metadata only) — incremental via checkpoint
        checkpoint = await sync_checkpoint_repository.get_or_create(db, repository.id)
        commits = await client.list_commits(
            owner, name, sha=default_branch, per_page=settings.GITHUB_SYNC_COMMIT_LIMIT
        )
        default_branch_row = await branch_repository.get_by_name(
            db, repository.id, default_branch
        )
        head_sha = commits[0]["sha"] if commits else None

        # Skip commit upserts when head matches last checkpoint (still refresh other metadata)
        if head_sha and checkpoint.last_commit_sha == head_sha:
            job.commits_synced = 0
            logger.info(
                "Incremental sync: commits unchanged",
                extra={"repository_id": str(repository.id), "sha": head_sha},
            )
        else:
            synced = 0
            for commit in commits:
                sha = commit["sha"]
                if checkpoint.last_commit_sha and sha == checkpoint.last_commit_sha:
                    break
                await self._upsert_commit(
                    db,
                    repository.id,
                    commit,
                    default_branch_row.id if default_branch_row else None,
                )
                synced += 1
            job.commits_synced = synced
            if head_sha:
                await sync_checkpoint_repository.update_checkpoint(
                    db,
                    repository.id,
                    last_commit_sha=head_sha,
                    last_sync_cursor=datetime.now(timezone.utc).isoformat(),
                )
        job.progress = 65
        await db.commit()

        # 7. Pull requests
        prs = await client.list_pull_requests(
            owner, name, per_page=settings.GITHUB_SYNC_PR_LIMIT
        )
        for pr in prs:
            await self._upsert_pull_request(db, repository.id, pr)
        job.pull_requests_synced = len(prs)
        job.progress = 80
        await db.commit()

        # 8. Issues (exclude PRs)
        issues = await client.list_issues(
            owner, name, per_page=settings.GITHUB_SYNC_ISSUE_LIMIT
        )
        issue_count = 0
        for issue in issues:
            if "pull_request" in issue:
                continue
            await self._upsert_issue(db, repository.id, issue)
            issue_count += 1
        job.issues_synced = issue_count
        job.progress = 90
        await db.commit()

        # 9. Contributors
        contributors = await client.list_contributors(owner, name)
        for contributor in contributors:
            if "login" not in contributor:
                continue
            await self._upsert_contributor(db, repository.id, contributor)
        job.contributors_synced = len(contributors)
        job.progress = 95
        await db.commit()

    async def _apply_repo_payload(
        self, db: AsyncSession, repository: Repository, remote: dict[str, Any]
    ) -> None:
        repository.name = remote.get("name") or repository.name
        repository.owner = (remote.get("owner") or {}).get("login") or repository.owner
        repository.full_name = remote.get("full_name") or repository.full_name
        repository.description = remote.get("description")
        repository.default_branch = remote.get("default_branch") or repository.default_branch
        repository.clone_url = remote.get("clone_url") or repository.clone_url
        repository.html_url = remote.get("html_url") or repository.html_url
        repository.provider_repository_id = str(remote.get("id") or repository.provider_repository_id)
        repository.external_id = str(remote.get("id") or repository.external_id)
        repository.visibility = (
            "private" if remote.get("private") else "public"
        )
        repository.stars_count = int(remote.get("stargazers_count") or 0)
        repository.forks_count = int(remote.get("forks_count") or 0)
        repository.watchers_count = int(remote.get("watchers_count") or 0)
        repository.open_issues_count = int(remote.get("open_issues_count") or 0)
        repository.size_kb = int(remote.get("size") or 0)
        license_info = remote.get("license") or {}
        repository.license = license_info.get("spdx_id") or license_info.get("name")
        repository.primary_language = remote.get("language")
        repository.is_archived = bool(remote.get("archived"))
        repository.is_fork = bool(remote.get("fork"))
        db.add(repository)

    async def _upsert_languages(
        self, db: AsyncSession, repository_id: uuid.UUID, languages: dict[str, int]
    ) -> None:
        total = sum(languages.values()) or 1
        rows = [
            RepositoryLanguage(
                repository_id=repository_id,
                language=lang,
                bytes=bytes_count,
                percentage=round((bytes_count / total) * 100, 2),
            )
            for lang, bytes_count in languages.items()
        ]
        await language_repository.replace_for_repository(db, repository_id, rows)

    async def _upsert_topics(
        self, db: AsyncSession, repository_id: uuid.UUID, topics: list[str]
    ) -> None:
        rows = [
            RepositoryTopic(repository_id=repository_id, topic=topic) for topic in topics
        ]
        await topic_repository.replace_for_repository(db, repository_id, rows)

    async def _upsert_branch(
        self,
        db: AsyncSession,
        repository_id: uuid.UUID,
        payload: dict[str, Any],
        default_branch: str,
    ) -> Branch:
        name = payload["name"]
        existing = await branch_repository.get_by_name(db, repository_id, name)
        sha = (payload.get("commit") or {}).get("sha")
        if existing:
            existing.latest_commit_sha = sha
            existing.is_default = name == default_branch
            existing.last_synced_at = datetime.now(timezone.utc)
            db.add(existing)
            return existing
        branch = Branch(
            repository_id=repository_id,
            name=name,
            is_default=name == default_branch,
            latest_commit_sha=sha,
            last_synced_at=datetime.now(timezone.utc),
        )
        db.add(branch)
        return branch

    async def _upsert_commit(
        self,
        db: AsyncSession,
        repository_id: uuid.UUID,
        payload: dict[str, Any],
        branch_id: uuid.UUID | None,
    ) -> Commit:
        sha = payload["sha"]
        existing = await commit_repository.get_by_sha(db, repository_id, sha)
        commit_info = payload.get("commit") or {}
        author = commit_info.get("author") or {}
        stats = payload.get("stats") or {}
        parents = payload.get("parents") or []
        values = {
            "branch_id": branch_id,
            "parent_commit_sha": parents[0]["sha"] if parents else None,
            "author_name": author.get("name"),
            "author_email": author.get("email"),
            "author_login": (payload.get("author") or {}).get("login"),
            "commit_message": commit_info.get("message"),
            "additions": stats.get("additions"),
            "deletions": stats.get("deletions"),
            "changed_files": stats.get("total"),
            "html_url": payload.get("html_url"),
            "committed_at": _parse_gh_datetime(author.get("date")),
            "synced_at": datetime.now(timezone.utc),
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            db.add(existing)
            return existing
        commit = Commit(repository_id=repository_id, commit_sha=sha, **values)
        db.add(commit)
        return commit

    async def _upsert_pull_request(
        self, db: AsyncSession, repository_id: uuid.UUID, payload: dict[str, Any]
    ) -> PullRequest:
        provider_id = str(payload["id"])
        from sqlalchemy import select

        result = await db.execute(
            select(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.provider_pr_id == provider_id,
            )
        )
        existing = result.scalars().first()
        status = PullRequestStatus.OPEN.value
        if payload.get("draft"):
            status = PullRequestStatus.DRAFT.value
        if payload.get("merged_at"):
            status = PullRequestStatus.MERGED.value
        elif payload.get("state") == "closed":
            status = PullRequestStatus.CLOSED.value

        values = {
            "number": payload["number"],
            "title": payload.get("title") or "",
            "description": payload.get("body"),
            "source_branch": (payload.get("head") or {}).get("ref"),
            "target_branch": (payload.get("base") or {}).get("ref"),
            "status": status,
            "author_login": (payload.get("user") or {}).get("login"),
            "author_avatar_url": (payload.get("user") or {}).get("avatar_url"),
            "html_url": payload.get("html_url"),
            "draft": bool(payload.get("draft")),
            "merged_at": _parse_gh_datetime(payload.get("merged_at")),
            "closed_at": _parse_gh_datetime(payload.get("closed_at")),
            "provider_created_at": _parse_gh_datetime(payload.get("created_at")),
            "provider_updated_at": _parse_gh_datetime(payload.get("updated_at")),
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            db.add(existing)
            return existing
        pr = PullRequest(
            repository_id=repository_id, provider_pr_id=provider_id, **values
        )
        db.add(pr)
        return pr

    async def _upsert_issue(
        self, db: AsyncSession, repository_id: uuid.UUID, payload: dict[str, Any]
    ) -> Issue:
        provider_id = str(payload["id"])
        from sqlalchemy import select

        result = await db.execute(
            select(Issue).filter(
                Issue.repository_id == repository_id,
                Issue.provider_issue_id == provider_id,
            )
        )
        existing = result.scalars().first()
        labels = [label.get("name") for label in (payload.get("labels") or []) if label.get("name")]
        values = {
            "number": payload["number"],
            "title": payload.get("title") or "",
            "body": payload.get("body"),
            "status": (
                IssueStatus.CLOSED.value
                if payload.get("state") == "closed"
                else IssueStatus.OPEN.value
            ),
            "author_login": (payload.get("user") or {}).get("login"),
            "author_avatar_url": (payload.get("user") or {}).get("avatar_url"),
            "html_url": payload.get("html_url"),
            "labels": json.dumps(labels),
            "closed_at": _parse_gh_datetime(payload.get("closed_at")),
            "provider_created_at": _parse_gh_datetime(payload.get("created_at")),
            "provider_updated_at": _parse_gh_datetime(payload.get("updated_at")),
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            db.add(existing)
            return existing
        issue = Issue(
            repository_id=repository_id, provider_issue_id=provider_id, **values
        )
        db.add(issue)
        return issue

    async def _upsert_contributor(
        self, db: AsyncSession, repository_id: uuid.UUID, payload: dict[str, Any]
    ) -> Contributor:
        provider_user_id = str(payload["id"])
        from sqlalchemy import select

        result = await db.execute(
            select(Contributor).filter(
                Contributor.repository_id == repository_id,
                Contributor.provider_user_id == provider_user_id,
            )
        )
        existing = result.scalars().first()
        values = {
            "login": payload["login"],
            "avatar_url": payload.get("avatar_url"),
            "html_url": payload.get("html_url"),
            "contributions": int(payload.get("contributions") or 0),
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            db.add(existing)
            return existing
        contributor = Contributor(
            repository_id=repository_id, provider_user_id=provider_user_id, **values
        )
        db.add(contributor)
        return contributor


sync_engine = SyncEngine()
