from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AdvisorChatRequest(BaseModel):
    message: str
    property_id: Optional[UUID] = None


class AdvisorMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime


class AdvisorHistoryResponse(BaseModel):
    thread_id: Optional[UUID]
    messages: list[AdvisorMessageResponse]
