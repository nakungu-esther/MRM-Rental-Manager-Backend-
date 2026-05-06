from __future__ import annotations

from pydantic import BaseModel


class MaintenanceCreate(BaseModel):
    unit_id: int
    title: str
    description: str | None = None
    priority: str = "medium"


class MaintenanceOut(BaseModel):
    id: int
    unit_id: int
    title: str
    description: str | None = None
    priority: str
    status: str
    cost_incurred: str

    model_config = {"from_attributes": True}

