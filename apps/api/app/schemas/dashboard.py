from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.schemas.evaluation import EvaluationScoresResponse


class TopPropertyItem(BaseModel):
    id: UUID
    address_street: str
    address_suburb: str
    listing_price_aud: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    status: str
    rank_position: Optional[int]
    family_fit_score: Optional[float]
    confidence_score: Optional[float]
    executive_summary: Optional[str]
    suburb_tier: Optional[str]
    scores: Optional[EvaluationScoresResponse]
    hero_image_url: Optional[str]


class UpcomingInspectionItem(BaseModel):
    id: UUID
    property_id: UUID
    property_address: str
    property_suburb: str
    scheduled_at: Optional[datetime]
    status: str


class DashboardResponse(BaseModel):
    family_display_name: str
    top_recommendations: list[TopPropertyItem]
    properties_reviewed: int
    new_this_week: int
    shortlist_count: int
    recent_journal_count: int
    upcoming_inspections: list[UpcomingInspectionItem] = []
