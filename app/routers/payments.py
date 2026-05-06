import os, uuid, shutil
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentOut
from app.services import payment_service
from app.config import settings
from app.utils.response import success_response, error_response

router = APIRouter(tags=["Payments"])


@router.get("/payments")
def list_payments(
    limit:  int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payments with standardized response"""
    payments = payment_service.get_all_payments(db, current_user.id, limit, offset)
    return success_response(data=payments)


@router.get("/tenants/{tenant_id}/payments")
def tenant_payments(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tenant payments with standardized response"""
    payments = payment_service.get_tenant_payments(db, tenant_id, current_user.id)
    return success_response(data=payments)


@router.post("/payments", status_code=201)
def record_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record payment with standardized response"""
    payment = payment_service.record_payment(db, data, current_user.id)
    return success_response(data=payment, message="Payment recorded successfully")


@router.patch("/payments/{payment_id}")
def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update payment with standardized response"""
    payment = payment_service.update_payment(db, payment_id, data, current_user.id)
    return success_response(data=payment, message="Payment updated successfully")


@router.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete payment with standardized response"""
    payment_service.delete_payment(db, payment_id, current_user.id)
    return success_response(message="Payment deleted successfully")


@router.get("/payments/{payment_id}/receipt")
def download_receipt(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf_path = payment_service.generate_receipt_pdf(db, payment_id, current_user.id, settings.upload_dir)
    full_path = pdf_path.replace("/uploads/", f"{settings.upload_dir}/")
    return FileResponse(
        full_path,
        media_type="application/pdf",
        filename=f"receipt_{payment_id:05d}.pdf",
    )


@router.post("/payments/{payment_id}/proof")
async def upload_proof(
    payment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload proof-of-payment image or PDF for an existing payment."""
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type not in allowed:
        raise error_response("Only JPEG, PNG, WebP, or PDF files allowed.", status_code=400)

    p = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.owner_id == current_user.id,
        Payment.is_deleted == False,
    ).first()
    if not p:
        raise error_response("Payment not found.", status_code=404)

    dest_dir = os.path.join(settings.upload_dir, "receipts", "proofs")
    os.makedirs(dest_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    fname = f"proof_{payment_id:05d}_{uuid.uuid4().hex[:8]}{ext}"
    with open(os.path.join(dest_dir, fname), "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Store proof path in the payment reference field if not already set
    proof_url = f"/uploads/receipts/proofs/{fname}"
    if not p.reference:
        p.reference = proof_url
    # Always store the latest proof path in notes if reference already used
    p.notes = (p.notes or "") + f"\n[proof:{proof_url}]"
    db.commit()

    payment = payment_service._enrich(payment_service._load(db, payment_id, current_user.id))
    return success_response(data=payment, message="Payment proof uploaded successfully")