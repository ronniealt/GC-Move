from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class JournalEntryCreate(BaseModel):
    entry_type: str = "note"
    title: Optional[str] = None
    body: str
    property_id: Optional[UUID] = None
    suburb_id: Optional[UUID] = None
    mood: Optional[str] = None
    tags: Optional[list[str]] = None
    is_pinned: bool = False


class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_id: UUID
    property_id: Optional[UUID]
    suburb_id: Optional[UUID]
    entry_type: str
    title: Optional[str]
    body: str
    mood: Optional[str]
    tags: Optional[list[str]]
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
