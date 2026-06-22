from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_id: UUID
    attribute: str
    category: str
    current_weight: float
    confidence: float
    status: str
    positive_signal_count: int
    negative_signal_count: int
    is_deal_breaker: bool
    notes: Optional[str] = None
    last_signal_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PreferenceUpdate(BaseModel):
    status: Optional[str] = None
    current_weight: Optional[float] = None
    is_deal_breaker: Optional[bool] = None
    notes: Optional[str] = None
