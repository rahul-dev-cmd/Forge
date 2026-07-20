from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        """
        Fetch a single entity by UUID, ignoring soft deleted records if the model supports it.
        """
        query = select(self.model).filter(self.model.id == id)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(getattr(self.model, "deleted_at") == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Fetch multiple entities with pagination support, filtering out soft deleted records.
        """
        query = select(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(getattr(self.model, "deleted_at") == None)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Insert a new database record.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update columns in a database record.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: UUID) -> ModelType | None:
        """
        Remove a database record, applying soft delete (populating deleted_at) if supported by the model.
        """
        db_obj = await self.get(db, id)
        if db_obj:
            if hasattr(db_obj, "deleted_at"):
                setattr(db_obj, "deleted_at", datetime.now(timezone.utc))
                db.add(db_obj)
            else:
                await db.delete(db_obj)
            await db.commit()
        return db_obj
