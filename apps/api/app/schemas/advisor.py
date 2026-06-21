from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AdvisorMessageRequest(BaseModel):
    content: str
    property_id: Optional[UUID] = None


class AdvisorMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    property_id: Optional[UUID]
    created_at: datetime


class AdvisorHistoryResponse(BaseModel):
    thread_id: UUID
    messages: list[AdvisorMessageResponse]
