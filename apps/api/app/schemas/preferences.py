from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attribute: str
    category: str
    current_weight: float
    confidence: float
    status: str
    positive_signal_count: int
    negative_signal_count: int
    is_deal_breaker: bool
    last_signal_at: Optional[datetime]


class PreferenceUpdateRequest(BaseModel):
    current_weight: Optional[float] = None
    status: Optional[str] = None
    is_deal_breaker: Optional[bool] = None
    notes: Optional[str] = None
