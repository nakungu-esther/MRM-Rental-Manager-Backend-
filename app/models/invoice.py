from sqlalchemy import Column, Integer, String, Numeric, Text, Enum, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    draft     = "draft"
    sent      = "sent"
    partial   = "partial"
    paid      = "paid"
    overdue   = "overdue"
    cancelled = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    lease_id   = Column(Integer, ForeignKey("leases.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id  = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id    = Column(Integer, ForeignKey("units.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    period_month   = Column(Integer, nullable=False)   # 1-12
    period_year    = Column(Integer, nullable=False)
    due_date       = Column(Date, nullable=False)

    # Amounts
    rent_amount    = Column(Numeric(12, 2), nullable=False)
    penalty_amount = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    total_amount   = Column(Numeric(12, 2), nullable=False)
    amount_paid    = Column(Numeric(12, 2), default=0)
    balance_due    = Column(Numeric(12, 2), nullable=False)

    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.draft, nullable=False)
    is_deleted = Column(Boolean, default=False)

    # Notes
    description = Column(Text, nullable=True)
    notes       = Column(Text, nullable=True)

    created_at  = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at  = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())
    sent_at     = Column(DateTime, nullable=True)
    paid_at     = Column(DateTime, nullable=True)

    # Relationships
    lease  = relationship("Lease", back_populates="invoices")
    tenant = relationship("Tenant", backref="invoices")
    unit   = relationship("Unit", backref="invoices")
