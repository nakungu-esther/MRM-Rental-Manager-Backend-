from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.tenant import Tenant, TenantStatus
from app.models.property import Unit, Property, UnitStatus
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.services.arrears_service import compute_tenant_balance

class TenantService:
    def _enrich(self, tenant: Tenant) -> dict:
        """Add computed/relational fields to tenant dict."""
        bal = compute_tenant_balance(tenant)
        return {
            **tenant.__dict__,
            "unit_number":   tenant.unit.unit_number if tenant.unit else None,
            "property_name": tenant.unit.property.name if tenant.unit and tenant.unit.property else None,
            "property_id":   tenant.unit.property.id if tenant.unit and tenant.unit.property else None,
            "balance_due":   bal["balance_due"],
            "months_in_arrears": bal["months_in_arrears"],
        }

    def _load(self, db: Session, tenant_id: int, owner_id: int) -> Tenant:
        t = (
            db.query(Tenant)
            .options(
                joinedload(Tenant.payments),
                joinedload(Tenant.unit).joinedload(Unit.property),
            )
            .filter(Tenant.id == tenant_id, Tenant.owner_id == owner_id)
            .first()
        )
        if not t:
            raise HTTPException(404, "Tenant not found")
        return t

    def get_all_tenants(
        self,
        db: Session,
        owner_id: int,
        search: str = "",
        status_filter: str = "",
        property_id: int = None,
    ) -> list:
        q = (
            db.query(Tenant)
            .options(
                joinedload(Tenant.payments),
                joinedload(Tenant.unit).joinedload(Unit.property),
            )
            .filter(Tenant.owner_id == owner_id)
        )
        if search:
            like = f"%{search}%"
            q = q.filter(
                Tenant.full_name.ilike(like) | Tenant.phone.ilike(like)
            )
        if status_filter:
            q = q.filter(Tenant.status == status_filter)
        if property_id:
            q = q.join(Unit).filter(Unit.property_id == property_id)

        return [self._enrich(t) for t in q.order_by(Tenant.created_at.desc()).all()]

    def get_tenant(self, db: Session, tenant_id: int, owner_id: int) -> dict:
        return self._enrich(self._load(db, tenant_id, owner_id))

    def create_tenant(self, db: Session, data: TenantCreate, owner_id: int) -> dict:
        # Verify unit belongs to owner and is vacant
        unit = db.query(Unit).join(Property).filter(
            Unit.id == data.unit_id,
            Property.owner_id == owner_id,
        ).first()
        
        if not unit:
            raise HTTPException(404, "Unit not found")
        if unit.status == UnitStatus.occupied:
            raise HTTPException(400, "Unit is already occupied")

        tenant = Tenant(owner_id=owner_id, **data.model_dump())
        db.add(tenant)

        # Mark unit occupied
        unit.status = UnitStatus.occupied
        db.commit()
        db.expire(tenant)

        # Create onboarding notification
        try:
            from app.models.notification import Notification, NotifType
            note = Notification(
                user_id=owner_id,
                title="New tenant added",
                message=f"{data.full_name} has been onboarded to unit {unit.unit_number}.",
                notif_type=NotifType.general,
                link=f"/tenants/{tenant.id}",
            )
            db.add(note)
            db.commit()
        except Exception:
            pass

        return self.get_tenant(db, tenant.id, owner_id)

    def update_tenant(self, db: Session, tenant_id: int, data: TenantUpdate, owner_id: int) -> dict:
        t = self._load(db, tenant_id, owner_id)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(t, k, v)
        db.commit()
        return self.get_tenant(db, tenant_id, owner_id)

    def move_out_tenant(self, db: Session, tenant_id: int, owner_id: int) -> dict:
        t = self._load(db, tenant_id, owner_id)
        t.status = TenantStatus.inactive
        if t.unit:
            t.unit.status = UnitStatus.vacant
        db.commit()
        return self.get_tenant(db, tenant_id, owner_id)

# CRITICAL: This line creates the instance that your router is looking for
tenant_service = TenantService()