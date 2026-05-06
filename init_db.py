"""
Initialize database tables.
Run this FIRST before running add_constraints.sql
"""
from app.database import engine, Base

# Import all models so SQLAlchemy knows about them
from app.models.user import User
from app.models.tenant import Tenant
from app.models.property import Property, Unit
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.maintenance import MaintenanceRequest
from app.models.notification import Notification
from app.models.audit import AuditLog

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Done! All tables created.")
print("\nNext step: Run database/add_constraints.sql to add constraints and indexes.")
