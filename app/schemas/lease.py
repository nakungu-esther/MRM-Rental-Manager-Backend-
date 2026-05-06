from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class LeaseCreate(BaseModel):
    tenant_id: int
    unit_id: int
    start_date: date
    end_date: Optional[date] = None
    monthly_rent: Decimal = Field(..., gt=0)
    deposit_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class LeaseUpdate(BaseModel):
    end_date: Optional[date] = None
    monthly_rent: Optional[Decimal] = Field(None, gt=0)
    deposit_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class LeaseTerminate(BaseModel):
    termination_date: date
    termination_reason: Optional[str] = None


class LeaseOut(BaseModel):
    id: int
    tenant_id: int
    unit_id: int
    owner_id: int
    start_date: date
    end_date: Optional[date]
    monthly_rent: Decimal
    deposit_amount: Optional[Decimal]
    deposit_paid: bool
    status: str
    termination_date: Optional[date]
    termination_reason: Optional[str]
    notes: Optional[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
