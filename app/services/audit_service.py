from __future__ import annotations

from sqlalchemy.orm import Session


def log_action(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    table_name: str | None = None,
    record_id: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
):
    from app.models.audit import AuditLog

    entry = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=None if old_value is None else str(old_value),
        new_value=None if new_value is None else str(new_value),
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

