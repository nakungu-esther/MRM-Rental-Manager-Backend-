from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.property import Property, Unit, UnitStatus

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # All active properties for this landlord
    properties = (
        db.query(Property)
        .filter(Property.owner_id == current_user.id, Property.is_active == True)
        .all()
    )

    total_properties = len(properties)
    property_ids = [p.id for p in properties]

    if not property_ids:
        return {
            "total_properties": 0,
            "total_units": 0,
            "occupied_units": 0,
            "vacant_units": 0,
            "maintenance_units": 0,
            "occupancy_rate": 0.0,
            "expected_monthly_rent": 0,
            "recent_properties": [],
        }

    # Unit counts
    units = db.query(Unit).filter(Unit.property_id.in_(property_ids)).all()
    total_units      = len(units)
    occupied_units   = sum(1 for u in units if u.status == UnitStatus.occupied)
    vacant_units     = sum(1 for u in units if u.status == UnitStatus.vacant)
    maintenance_units= sum(1 for u in units if u.status == UnitStatus.maintenance)
    occupancy_rate   = round((occupied_units / total_units * 100), 1) if total_units else 0.0
    expected_rent    = sum(float(u.rent_amount) for u in units if u.status == UnitStatus.occupied)

    # 3 most recent properties
    recent = sorted(properties, key=lambda p: p.created_at or 0, reverse=True)[:3]
    recent_properties = [
        {
            "id":              p.id,
            "name":            p.name,
            "address":         p.address,
            "photo_path":      p.photo_path,
            "total_units":     len(p.units),
            "occupied_units":  sum(1 for u in p.units if u.status == UnitStatus.occupied),
            "occupancy_rate":  round((sum(1 for u in p.units if u.status == UnitStatus.occupied) / len(p.units) * 100), 1) if p.units else 0.0,
        }
        for p in recent
    ]

    return {
        "total_properties":    total_properties,
        "total_units":         total_units,
        "occupied_units":      occupied_units,
        "vacant_units":        vacant_units,
        "maintenance_units":   maintenance_units,
        "occupancy_rate":      occupancy_rate,
        "expected_monthly_rent": expected_rent,
        "recent_properties":   recent_properties,
    }