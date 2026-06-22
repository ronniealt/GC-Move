from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SchoolMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    naplan_reading_pct_above_nms: Optional[float] = None
    naplan_numeracy_pct_above_nms: Optional[float] = None
    wellbeing_score: Optional[float] = None
    parent_community_score: Optional[float] = None
    academic_outcomes_score: Optional[float] = None
    commute_score: Optional[float] = None
    extracurricular_score: Optional[float] = None
    pathway_score: Optional[float] = None
    school_score: Optional[float] = None
    attendance_rate_pct: Optional[float] = None
    annual_fee_aud: Optional[int] = None
    has_boarding: bool = False
    extracurricular_notes: Optional[str] = None
    data_year: Optional[int] = None


class SchoolListItem(BaseModel):
    id: UUID
    name: str
    school_type: str
    sector: str
    address_suburb: str
    address_postcode: Optional[str] = None
    year_range: Optional[str] = None
    icsea: Optional[int] = None
    total_enrolments: Optional[int] = None
    website_url: Optional[str] = None
    metrics: Optional[SchoolMetricResponse] = None
