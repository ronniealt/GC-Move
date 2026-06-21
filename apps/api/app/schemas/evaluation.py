from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class EvaluationScoresResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    community_score: Optional[float]
    lifestyle_score: Optional[float]
    school_score: Optional[float]
    property_score: Optional[float]
    financial_score: Optional[float]
    risk_score: Optional[float]
    family_fit_score: Optional[float]
    five_year_fit_score: Optional[float]


class MemberCommentaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: UUID
    commentary: str
    key_positives: Optional[list[str]]
    key_concerns: Optional[list[str]]
    fit_score: Optional[float]


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    evaluation_version: str
    evaluated_at: datetime
    is_current: bool
    confidence_score: float
    executive_summary: Optional[str]
    community_narrative: Optional[str]
    lifestyle_narrative: Optional[str]
    school_narrative: Optional[str]
    property_narrative: Optional[str]
    financial_narrative: Optional[str]
    five_year_narrative: Optional[str]
    deal_breakers_flagged: Optional[list[str]]
    scores: Optional[EvaluationScoresResponse]
    per_member: list[MemberCommentaryResponse] = []


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    rank_position: Optional[int]
    family_fit_score: Optional[float]
    score_delta: Optional[float]
    status: str
    headline: Optional[str]
    summary: Optional[str]
    ranked_at: datetime
