from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class EvaluationScoresResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    community_score: Optional[float] = None
    lifestyle_score: Optional[float] = None
    school_score: Optional[float] = None
    property_score: Optional[float] = None
    financial_score: Optional[float] = None
    risk_score: Optional[float] = None
    family_fit_score: Optional[float] = None
    five_year_fit_score: Optional[float] = None
    # Community sub-scores
    owner_occupier_score: Optional[float] = None
    family_density_score: Optional[float] = None
    educational_attainment_score: Optional[float] = None
    median_income_score: Optional[float] = None
    crime_score: Optional[float] = None
    community_engagement_score: Optional[float] = None
    # Lifestyle sub-scores
    burleigh_access_score: Optional[float] = None
    beach_access_score: Optional[float] = None
    wellness_score: Optional[float] = None
    cafe_dining_score: Optional[float] = None
    outdoor_recreation_score: Optional[float] = None
    shopping_score: Optional[float] = None
    # School sub-scores
    wellbeing_score: Optional[float] = None
    parent_community_score: Optional[float] = None
    academic_outcomes_score: Optional[float] = None
    school_commute_score: Optional[float] = None
    extracurricular_score: Optional[float] = None
    school_pathway_score: Optional[float] = None
    # Property sub-scores
    modernity_score: Optional[float] = None
    design_quality_score: Optional[float] = None
    indoor_outdoor_flow_score: Optional[float] = None
    pool_quality_score: Optional[float] = None
    home_office_score: Optional[float] = None
    entertaining_space_score: Optional[float] = None
    privacy_score: Optional[float] = None
    block_utility_score: Optional[float] = None


class MemberCommentaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: UUID
    commentary: str
    key_positives: Optional[list[str]] = None
    key_concerns: Optional[list[str]] = None
    fit_score: Optional[float] = None


class RecommendationExplanationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dimension: str
    explanation: str
    score: Optional[float] = None


class FullEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evaluation_id: UUID
    property_id: UUID
    recommendation_level: Optional[str] = None
    meets_non_negotiables: Optional[bool] = None
    evaluated_at: datetime
    confidence_score: float
    # Narratives
    executive_summary: Optional[str] = None
    community_narrative: Optional[str] = None
    lifestyle_narrative: Optional[str] = None
    school_narrative: Optional[str] = None
    property_narrative: Optional[str] = None
    financial_narrative: Optional[str] = None
    five_year_narrative: Optional[str] = None
    deal_breakers_flagged: Optional[list[str]] = None
    action_plan: Optional[dict[str, Any]] = None
    # Scores
    scores: Optional[EvaluationScoresResponse] = None
    # Per-member
    per_member: list[MemberCommentaryResponse] = []
    # Recommendation
    recommendation_headline: Optional[str] = None
    recommendation_summary: Optional[str] = None
    family_fit_score: Optional[float] = None
    # Explanations
    explanations: list[RecommendationExplanationResponse] = []


# Legacy schemas kept for backward compat
class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    evaluation_version: str
    evaluated_at: datetime
    is_current: bool
    confidence_score: float
    recommendation_level: Optional[str] = None
    meets_non_negotiables: Optional[bool] = None
    executive_summary: Optional[str] = None
    community_narrative: Optional[str] = None
    lifestyle_narrative: Optional[str] = None
    school_narrative: Optional[str] = None
    property_narrative: Optional[str] = None
    financial_narrative: Optional[str] = None
    five_year_narrative: Optional[str] = None
    deal_breakers_flagged: Optional[list[str]] = None
    action_plan: Optional[dict[str, Any]] = None
    scores: Optional[EvaluationScoresResponse] = None
    per_member: list[MemberCommentaryResponse] = []


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    rank_position: Optional[int] = None
    family_fit_score: Optional[float] = None
    score_delta: Optional[float] = None
    status: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    ranked_at: datetime
