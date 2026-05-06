"""
Users Router — profile management for the authenticated user.
"""
from __future__ import annotations

import os, uuid, shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserOut
from app.config import settings

router = APIRouter(prefix="/users", tags=["Users"])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone:     Optional[str] = None


@router.get("/me", response_model=UserOut, summary="Get current user profile")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut, summary="Update name / phone")
def update_me(
    data:         ProfileUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    if data.full_name:
        current_user.full_name = data.full_name.strip()
    if data.phone:
        current_user.phone = data.phone.strip()
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password", summary="Change password (requires current password)")
def change_password(
    current_password: str  = Form(...),
    new_password:     str  = Form(...),
    db:               Session = Depends(get_db),
    current_user:     User    = Depends(get_current_user),
):
    from app.services.auth_service import auth_service
    if not auth_service.verify_password(current_password, current_user.password_hash):
        raise HTTPException(400, "Current password is incorrect.")
    if len(new_password) < 6:
        raise HTTPException(400, "New password must be at least 6 characters.")
    auth_service.set_password(db, current_user, new_password)
    return {"message": "Password changed successfully."}
