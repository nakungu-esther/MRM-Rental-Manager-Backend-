from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationOut(BaseModel):
    id:         int
    user_id:    int
    title:      str
    message:    str
    notif_type: str
    is_read:    bool
    link:       Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    title:      str
    message:    str
    notif_type: Optional[str] = "general"
    link:       Optional[str] = None