from typing import Any, List
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository

class AuditLogRepository(BaseRepository[AuditLog, Any, Any]):
    def __init__(self):
        super().__init__(AuditLog)

    async def get_by_actor(
        self, db: AsyncSession, actor_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        Fetch audit logs created by a specific user ID, ordered by date (newest first).
        """
        query = select(AuditLog).filter(
            AuditLog.actor_id == actor_id
        ).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_target(
        self, db: AsyncSession, target_type: str, target_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        Fetch audit logs associated with a target entity ID.
        """
        query = select(AuditLog).filter(
            AuditLog.target_type == target_type,
            AuditLog.target_id == target_id
        ).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

audit_log_repository = AuditLogRepository()
