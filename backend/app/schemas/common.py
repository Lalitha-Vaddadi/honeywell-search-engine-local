from pydantic import BaseModel
from typing import Any, Optional, List


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
