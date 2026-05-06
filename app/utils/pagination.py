from __future__ import annotations

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int

