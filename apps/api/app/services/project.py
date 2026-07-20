import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project, ProjectSettings
from app.models.audit_log import AuditLog
from app.models.enums import ProjectStatus, ProjectPriority
from app.utils.query_builder import build_and_execute_query
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    priority: str = ProjectPriority.MEDIUM.value
    visibility: str = "private"
    tags: List[str] = []

class ProjectUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    tags: List[str] | None = None
    due_date: datetime | None = None
    visibility: str | None = None
    is_favorite: bool | None = None
    version: int # Enforced for optimistic concurrency locking checks

class ProjectService:
    async def create_project(self, db: AsyncSession, project_in: ProjectCreate, ip_address: str | None = None) -> Project:
        """
        Create a project inside a workspace, validate unique name, set defaults, and audit log it.
        """
        # 1. Enforce unique project name inside the workspace
        dup_query = select(Project).filter(
            Project.workspace_id == project_in.workspace_id,
            Project.name == project_in.name,
            Project.deleted_at == None
        )
        dup_res = await db.execute(dup_query)
        if dup_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with name '{project_in.name}' already exists in this workspace."
            )

        # 2. Enforce unique project slug inside the workspace
        dup_slug_query = select(Project).filter(
            Project.workspace_id == project_in.workspace_id,
            Project.slug == project_in.slug,
            Project.deleted_at == None
        )
        dup_slug_res = await db.execute(dup_slug_query)
        if dup_slug_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with slug '{project_in.slug}' already exists in this workspace."
            )

        # Create Project
        project = Project(
            workspace_id=project_in.workspace_id,
            owner_id=project_in.owner_id,
            name=project_in.name,
            slug=project_in.slug,
            description=project_in.description,
            priority=project_in.priority,
            visibility=project_in.visibility,
            tags=project_in.tags,
            status=ProjectStatus.ACTIVE.value,
            version=1
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # Create Settings
        settings_obj = ProjectSettings(
            project_id=project.id,
            default_branch="main",
            coding_style="standard",
            preferred_language="python",
            ai_enabled=True
        )
        db.add(settings_obj)

        # Write audit trail
        log = AuditLog(
            actor_id=project_in.owner_id,
            action="project_creation",
            target_type="project",
            target_id=project.id,
            details={"name": project.name, "slug": project.slug},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(project)
        return project

    async def get_project_by_id_or_slug(self, db: AsyncSession, id_or_slug: str, workspace_id: uuid.UUID) -> Project | None:
        """
        Fetch project by either its UUID or its unique workspace slug.
        """
        try:
            p_uuid = uuid.UUID(id_or_slug)
            query = select(Project).filter(Project.id == p_uuid, Project.deleted_at == None)
        except ValueError:
            query = select(Project).filter(
                Project.workspace_id == workspace_id,
                Project.slug == id_or_slug,
                Project.deleted_at == None
            )
            
        result = await db.execute(query)
        return result.scalars().first()

    async def get_project(self, db: AsyncSession, project_id: uuid.UUID) -> Project | None:
        """
        Fetch project by UUID.
        """
        query = select(Project).filter(Project.id == project_id, Project.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def query_projects(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        *,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        favorite_only: Optional[bool] = None,
        sort_by: Optional[str] = "created_at",
        order: str = "desc",
        page: int = 1,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Tuple[List[Project], int, Optional[str]]:
        """
        Modular query manager wrapper executing filters, sorting and pagination on project records.
        """
        base_q = select(Project).filter(Project.workspace_id == workspace_id)
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if priority_filter:
            filters["priority"] = priority_filter
        if favorite_only is not None:
            filters["is_favorite"] = favorite_only
            
        return await build_and_execute_query(
            db,
            Project,
            base_query=base_q,
            search_query=search_query,
            search_fields=["name", "description", "slug"],
            filters=filters,
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit,
            cursor=cursor,
            cursor_field="created_at"
        )

    async def update_project(
        self, db: AsyncSession, project_id: uuid.UUID, project_in: ProjectUpdate, actor_id: uuid.UUID, ip_address: str | None = None
    ) -> Project:
        """
        Update project variables, validating version context to prevent stale concurrency conflicts.
        """
        project = await self.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        # Concurrency verification: Reject stale updates
        if project.version != project_in.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict: Project has been modified by another user. Please refresh and try again."
            )

        update_data = project_in.model_dump(exclude_unset=True)
        update_data.pop("version", None)

        for field in update_data:
            if hasattr(project, field):
                setattr(project, field, update_data[field])

        project.version += 1
        db.add(project)

        log = AuditLog(
            actor_id=actor_id,
            action="project_update",
            target_type="project",
            target_id=project_id,
            details=update_data,
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(project)
        return project

    async def archive_project(self, db: AsyncSession, project_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None) -> Project:
        """
        Archive project profile settings.
        """
        project = await self.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        project.status = ProjectStatus.ARCHIVED.value
        project.archived_at = datetime.now(timezone.utc)
        db.add(project)

        log = AuditLog(
            actor_id=actor_id,
            action="project_archived",
            target_type="project",
            target_id=project_id,
            details={"name": project.name},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(project)
        return project

    async def restore_project(self, db: AsyncSession, project_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None) -> Project:
        """
        Restore an archived project back to active.
        """
        project = await db.get(Project, project_id)
        if not project or project.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        project.status = ProjectStatus.ACTIVE.value
        project.archived_at = None
        db.add(project)

        log = AuditLog(
            actor_id=actor_id,
            action="project_restored",
            target_type="project",
            target_id=project_id,
            details={"name": project.name},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(project)
        return project

    async def bulk_archive_projects(
        self, db: AsyncSession, project_ids: List[uuid.UUID], actor_id: uuid.UUID, ip_address: str | None = None
    ) -> int:
        """
        Bulk archive multiple projects.
        """
        count = 0
        for pid in project_ids:
            try:
                await self.archive_project(db, pid, actor_id, ip_address)
                count += 1
            except HTTPException:
                pass
        return count

    async def delete_project(self, db: AsyncSession, project_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None) -> Project:
        """
        Soft delete project and audit log the action.
        """
        project = await self.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        project.deleted_at = datetime.now(timezone.utc)
        project.deleted_by = actor_id
        db.add(project)

        log = AuditLog(
            actor_id=actor_id,
            action="project_deletion",
            target_type="project",
            target_id=project_id,
            details={"name": project.name},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        return project

project_service = ProjectService()
