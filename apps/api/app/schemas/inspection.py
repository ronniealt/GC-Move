from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class InspectionPropertySnippet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    address_street: str
    address_suburb: str


class InspectionCreate(BaseModel):
    property_id: UUID
    scheduled_at: datetime
    notes: Optional[str] = None
    inspection_type: str = "open_home"


class InspectionUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    overall_impression: Optional[str] = None


class InspectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_id: UUID
    property_id: UUID
    inspection_type: str
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    overall_impression: Optional[str] = None
    notes: Optional[str] = None
    property: Optional[InspectionPropertySnippet] = None
    created_at: datetime
    updated_at: datetime
