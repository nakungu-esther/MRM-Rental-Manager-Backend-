from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routers import auth, properties, dashboard, tenants, payments, notifications, maintenance, users, tenant_portal, leases, invoices

# Ensure upload subdirectories exist
for sub in ["properties", "tenants", "receipts", "receipts/proofs", "maintenance"]:
    os.makedirs(os.path.join(settings.upload_dir, sub), exist_ok=True)

app = FastAPI(
    title="RentalMGR API",
    version="1.0.0",
    description="MRM Rental Manager — Property, Tenant & Payment Management API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

API = "/api/v1"
app.include_router(auth.router,         prefix=API)
app.include_router(users.router,        prefix=API)
app.include_router(properties.router,   prefix=API)
app.include_router(dashboard.router,    prefix=API)
app.include_router(tenants.router,      prefix=API)
app.include_router(payments.router,     prefix=API)
app.include_router(maintenance.router,  prefix=API)
app.include_router(notifications.router, prefix=API)
app.include_router(tenant_portal.router,  prefix=API)
app.include_router(leases.router,       prefix=API)
app.include_router(invoices.router,     prefix=API)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}