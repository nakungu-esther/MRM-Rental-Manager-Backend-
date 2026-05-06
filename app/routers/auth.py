from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserOut,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest,
)
from app.services.auth_service import auth_service
from app.services.email_service import (
    generate_otp, send_registration_verification_link, send_password_reset_otp,
    generate_verification_token
)
from app.dependencies import get_current_user
from app.models.user import User
from app.utils.security import decode_token
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/auth", tags=["Auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


# ── REGISTER (step 1) ─────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # Check duplicate
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "An account with this email already exists.")

    token = generate_verification_token()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=15)

    user = auth_service.create_user(db, payload, verification_token=token, token_expiry=expiry)

    sent = send_registration_verification_link(user.email, user.full_name, token)
    if not sent:
        # Still return success — user can request resend
        # but log for admin
        print(f"[WARN] Could not send verification email to {user.email}. Token: {token}")

    return {
        "message": "Account created. Please check your email for a verification link.",
        "email": user.email,
    }


# ── VERIFY EMAIL via Link (GET request for email links) ────────────
@router.get("/verify-email")
def verify_email_link(email: str, token: str, db: Session = Depends(get_db)):
    """Verify email via link click. Redirects to frontend with success/error message."""
    from fastapi.responses import RedirectResponse
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url=f"http://localhost:5174/login?error=account_not_found")
    
    if user.email_verified:
        return RedirectResponse(url=f"http://localhost:5174/login?message=already_verified")

    if not user.verification_token or user.verification_token != token:
        return RedirectResponse(url=f"http://localhost:5174/login?error=invalid_token")

    expiry = user.verification_token_expiry
    if expiry:
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            return RedirectResponse(url=f"http://localhost:5174/login?error=token_expired")

    user.email_verified = True
    user.verification_token = None
    user.verification_token_expiry = None
    db.commit()

    return RedirectResponse(url=f"http://localhost:5174/login?verified=true&email={email}")


# ── LOGIN ─────────────────────────────────────────────────────────
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise error_response("Invalid email or password.", status_code=401)
    if not user.is_active:
        raise error_response("Account is disabled. Contact support.", status_code=403)
    if not user.email_verified:
        raise error_response("Please verify your email before logging in.", status_code=403)

    tokens = auth_service.create_tokens(db, user)
    return success_response(
        data={
            "access_token": tokens["access_token"],
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
            }
        }
    )


# ── REFRESH ───────────────────────────────────────────────────────
@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Accept refresh_token in request body (matches frontend client.js)."""
    token = payload.refresh_token
    decoded = decode_token(token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user_id = decoded.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    # Verify token matches stored refresh token
    if user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Refresh token revoked.")

    tokens = auth_service.create_tokens(db, user)
    return tokens


# ── LOGOUT ────────────────────────────────────────────────────────
@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.refresh_token = None
    db.commit()
    return {"message": "Logged out."}


# ── FORGOT PASSWORD ───────────────────────────────────────────────
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If that email exists, a reset code has been sent."}

    otp = generate_otp()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    user.reset_otp = otp
    user.reset_otp_expiry = expiry
    db.commit()

    sent = send_password_reset_otp(user.email, otp)
    if not sent:
        print(f"[WARN] Could not send reset OTP to {user.email}. OTP: {otp}")

    return {"message": "If that email exists, a reset code has been sent."}


# ── RESET PASSWORD ────────────────────────────────────────────────
@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(404, "Account not found.")

    if not user.reset_otp or user.reset_otp != payload.otp:
        raise HTTPException(400, "Invalid or expired reset code.")

    expiry = user.reset_otp_expiry
    if expiry:
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            raise HTTPException(400, "Reset code has expired. Request a new one.")

    auth_service.set_password(db, user, payload.new_password)
    user.reset_otp = None
    user.reset_otp_expiry = None
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}


# ── ME ────────────────────────────────────────────────────────────
@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success_response(
        data={
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        }
    )