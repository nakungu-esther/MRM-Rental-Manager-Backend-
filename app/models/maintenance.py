from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id              = Column(Integer, primary_key=True)
    unit_id         = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    reported_by     = Column(Integer, ForeignKey("users.id"))
    title           = Column(String(200), nullable=False)
    description     = Column(Text)
    priority        = Column(String(16), default="medium")  # low|medium|high|urgent
    status          = Column(String(16), default="open")    # open|in_progress|resolved|closed
    cost_incurred   = Column(String(32), default="0")
    resolution_note = Column(Text)
    photo_path      = Column(String(500))
    resolved_at     = Column(DateTime)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow)

    # Relationships
    unit = relationship("Unit", backref="maintenance_requests", lazy="select")
