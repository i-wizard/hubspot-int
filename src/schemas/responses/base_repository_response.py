from typing import Optional, Any, Dict

from pydantic import BaseModel


class RepositoryResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    details: Optional[Any] = None
