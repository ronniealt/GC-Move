from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SuburbResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    postcode: str
    state: str
    latitude: float
    longitude: float
    tier: Optional[str]
    is_active: bool
    community_score: Optional[float] = None
    lifestyle_score: Optional[float] = None


class SchoolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    school_type: str
    sector: str
    address_suburb: str
    address_postcode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    year_range: Optional[str]
    total_enrolments: Optional[int]
    icsea: Optional[int]
    website_url: Optional[str]
    school_score: Optional[float] = None
