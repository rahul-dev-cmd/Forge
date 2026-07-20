import base64
from datetime import datetime
from typing import Any, List, Optional, Tuple, Type, TypeVar
from sqlalchemy import select, func, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)

def encode_cursor(value: Any) -> str:
    """
    Encode an attribute value to a base64 cursor string.
    """
    if value is None:
        return ""
    if isinstance(value, datetime):
        val_str = f"datetime:{value.isoformat()}"
    else:
        val_str = f"raw:{str(value)}"
    return base64.b64encode(val_str.encode("utf-8")).decode("utf-8")

def decode_cursor(cursor_str: str) -> Tuple[str, Any]:
    """
    Decode a base64 cursor string to its raw type and value.
    """
    try:
        decoded = base64.b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        prefix, value = decoded.split(":", 1)
        if prefix == "datetime":
            return prefix, datetime.fromisoformat(value)
        return prefix, value
    except Exception:
        return "invalid", None

async def build_and_execute_query(
    db: AsyncSession,
    model: Type[ModelType],
    *,
    base_query: Any = None,
    search_query: Optional[str] = None,
    search_fields: List[str] = [],
    filters: dict = {},
    sort_by: Optional[str] = None,
    order: str = "asc",
    page: int = 1,
    limit: int = 20,
    cursor: Optional[str] = None,
    cursor_field: str = "created_at"
) -> Tuple[List[ModelType], int, Optional[str]]:
    """
    Universal query manager supporting:
    - Search queries ilike across multiple fields
    - Precise dictionary filters (skipping None values)
    - Sorting by column in asc/desc modes
    - Dual modes pagination: Offset-based (page/limit) or Cursor-based (cursor)
    
    Returns: Tuple[items_list, total_count, next_cursor_string]
    """
    # 1. Initialize base query
    stmt = base_query if base_query is not None else select(model)
    
    # 2. Apply Soft Delete filter if present
    if hasattr(model, "deleted_at"):
        stmt = stmt.filter(getattr(model, "deleted_at") == None)
        
    # 3. Apply exact dictionary matches
    for col_name, val in filters.items():
        if val is not None and hasattr(model, col_name):
            stmt = stmt.filter(getattr(model, col_name) == val)

    # 4. Apply search queries
    if search_query and search_fields:
        search_filter = f"%{search_query}%"
        or_conditions = []
        for field in search_fields:
            if hasattr(model, field):
                or_conditions.append(getattr(model, field).ilike(search_filter))
        if or_conditions:
            stmt = stmt.filter(or_(*or_conditions))

    # 5. Evaluate total count (before pagination)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # 6. Apply Sorting
    sort_col = getattr(model, sort_by) if sort_by and hasattr(model, sort_by) else getattr(model, cursor_field)
    sort_direction = asc(sort_col) if order.lower() == "asc" else desc(sort_col)
    stmt = stmt.order_by(sort_direction)

    # 7. Apply Pagination (Cursor-based takes priority if cursor is sent)
    next_cursor = None
    if cursor:
        prefix, cursor_val = decode_cursor(cursor)
        if cursor_val is not None:
            if order.lower() == "asc":
                stmt = stmt.filter(sort_col > cursor_val)
            else:
                stmt = stmt.filter(sort_col < cursor_val)
        # Limit to fetch current page plus 1 extra element to compute next cursor
        stmt = stmt.limit(limit + 1)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        
        if len(items) > limit:
            # We have more elements; extract the next cursor value from the last element (index: limit - 1)
            last_item = items[limit - 1]
            last_val = getattr(last_item, sort_by if sort_by and hasattr(last_item, sort_by) else cursor_field)
            next_cursor = encode_cursor(last_val)
            items = items[:limit] # return original limit size
    else:
        # Fall back to standard offset pagination
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        
    return items, total_count, next_cursor
