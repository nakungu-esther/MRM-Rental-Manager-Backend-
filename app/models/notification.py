from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class NotifType(str, enum.Enum):
    payment_received = "payment_received"
    rent_due         = "rent_due"
    lease_expiring   = "lease_expiring"
    arrears          = "arrears"
    general          = "general"


class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title      = Column(String(200), nullable=False)
    message    = Column(Text, nullable=False)
    notif_type = Column(Enum(NotifType), default=NotifType.general)
    is_read    = Column(Boolean, default=False)
    link       = Column(String(300), nullable=True)   # e.g. /tenants/5
    created_at = Column(DateTime, default=func.now(), server_default=func.now())