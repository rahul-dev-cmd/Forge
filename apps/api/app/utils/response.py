from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

DataType = TypeVar("DataType")

class ResponseMeta(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None
    cursor: Optional[str] = None

class ResponseEnvelope(BaseModel, Generic[DataType]):
    success: bool = True
    data: DataType
    message: str = ""
    meta: Optional[ResponseMeta] = None

def wrap_response(
    data: Any,
    message: str = "",
    success: bool = True,
    page: Optional[int] = None,
    limit: Optional[int] = None,
    total: Optional[int] = None,
    cursor: Optional[str] = None
) -> dict:
    """
    Format data using the standardized API response envelope.
    """
    meta_payload = None
    if any(v is not None for v in [page, limit, total, cursor]):
        meta_payload = {
            "page": page,
            "limit": limit,
            "total": total,
            "cursor": cursor
        }
        
    return {
        "success": success,
        "data": data,
        "message": message,
        "meta": meta_payload
    }
