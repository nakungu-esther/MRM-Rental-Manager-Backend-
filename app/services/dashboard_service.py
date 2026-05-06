from __future__ import annotations

from app.schemas.dashboard import DashboardStats


def get_dashboard_stats() -> DashboardStats:
    return DashboardStats()

