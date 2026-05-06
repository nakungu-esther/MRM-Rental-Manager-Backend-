from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["units"])


@router.get("/units/health")
def units_health():
    return {"ok": True}

