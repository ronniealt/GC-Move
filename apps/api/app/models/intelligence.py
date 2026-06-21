import uuid
from sqlalchemy import (
    Boolean, Column, CheckConstraint, DateTime, ForeignKey,
    Integer, Numeric, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class PropertyEvaluation(TimestampMixin, Base):
    __tablename__ = "property_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"))
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"))
    evaluation_version = Column(Text, nullable=False, default="v1")
    openai_model = Column(Text, nullable=False, default="gpt-4o")
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_current = Column(Boolean, nullable=False, default=True)
    confidence_score = Column(Numeric(3, 2), nullable=False)
    executive_summary = Column(Text)
    community_narrative = Column(Text)
    lifestyle_narrative = Column(Text)
    school_narrative = Column(Text)
    property_narrative = Column(Text)
    financial_narrative = Column(Text)
    five_year_narrative = Column(Text)
    deal_breakers_flagged = Column(ARRAY(Text))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_cost_usd = Column(Numeric(8, 4))

    scores = relationship("EvaluationScore", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
    per_member = relationship("EvaluationPerMember", back_populates="evaluation", cascade="all, delete-orphan")
    recommendation = relationship("Recommendation", back_populates="evaluation", uselist=False)


class EvaluationScore(Base):
    __tablename__ = "evaluation_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("property_evaluations.id", ondelete="CASCADE"), nullable=False, unique=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    community_score = Column(Numeric(4, 2))
    lifestyle_score = Column(Numeric(4, 2))
    school_score = Column(Numeric(4, 2))
    property_score = Column(Numeric(4, 2))
    financial_score = Column(Numeric(4, 2))
    risk_score = Column(Numeric(4, 2))
    family_fit_score = Column(Numeric(5, 2))
    five_year_fit_score = Column(Numeric(5, 2))
    # Community sub-scores
    owner_occupier_score = Column(Numeric(4, 2))
    family_density_score = Column(Numeric(4, 2))
    educational_attainment_score = Column(Numeric(4, 2))
    median_income_score = Column(Numeric(4, 2))
    crime_score = Column(Numeric(4, 2))
    community_engagement_score = Column(Numeric(4, 2))
    # Lifestyle sub-scores
    burleigh_access_score = Column(Numeric(4, 2))
    beach_access_score = Column(Numeric(4, 2))
    wellness_score = Column(Numeric(4, 2))
    cafe_dining_score = Column(Numeric(4, 2))
    outdoor_recreation_score = Column(Numeric(4, 2))
    shopping_score = Column(Numeric(4, 2))
    # School sub-scores
    wellbeing_score = Column(Numeric(4, 2))
    parent_community_score = Column(Numeric(4, 2))
    academic_outcomes_score = Column(Numeric(4, 2))
    school_commute_score = Column(Numeric(4, 2))
    extracurricular_score = Column(Numeric(4, 2))
    school_pathway_score = Column(Numeric(4, 2))
    # Property sub-scores
    modernity_score = Column(Numeric(4, 2))
    design_quality_score = Column(Numeric(4, 2))
    indoor_outdoor_flow_score = Column(Numeric(4, 2))
    pool_quality_score = Column(Numeric(4, 2))
    home_office_score = Column(Numeric(4, 2))
    entertaining_space_score = Column(Numeric(4, 2))
    privacy_score = Column(Numeric(4, 2))
    block_utility_score = Column(Numeric(4, 2))
    weights_snapshot = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    evaluation = relationship("PropertyEvaluation", back_populates="scores")


class EvaluationPerMember(Base):
    __tablename__ = "evaluation_per_member"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("property_evaluations.id", ondelete="CASCADE"), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    commentary = Column(Text, nullable=False)
    key_positives = Column(ARRAY(Text))
    key_concerns = Column(ARRAY(Text))
    fit_score = Column(Numeric(4, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    evaluation = relationship("PropertyEvaluation", back_populates="per_member")
    member = relationship("FamilyMember")


class Recommendation(TimestampMixin, Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("property_evaluations.id"), nullable=False)
    rank_position = Column(Integer)
    family_fit_score = Column(Numeric(5, 2))
    previous_rank = Column(Integer)
    score_delta = Column(Numeric(5, 2))
    status = Column(Text, nullable=False, default="active")
    headline = Column(Text)
    summary = Column(Text)
    ranked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("family_id", "property_id", name="recommendations_family_property_unique"),
        CheckConstraint("status IN ('active', 'archived', 'dismissed', 'accepted')", name="recommendations_status_check"),
    )

    evaluation = relationship("PropertyEvaluation", back_populates="recommendation")
    explanations = relationship("RecommendationExplanation", back_populates="recommendation", cascade="all, delete-orphan")


class RecommendationExplanation(Base):
    __tablename__ = "recommendation_explanations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    dimension = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    score = Column(Numeric(4, 2))
    supporting_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "dimension IN ('community', 'lifestyle', 'school', 'property', 'financial', 'family_fit', 'risk')",
            name="recommendation_explanations_dimension_check",
        ),
    )

    recommendation = relationship("Recommendation", back_populates="explanations")


class PreferenceEvent(Base):
    __tablename__ = "preference_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"))
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"))
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"))
    attribute = Column(Text, nullable=False)
    sentiment = Column(Text, nullable=False)
    strength = Column(Integer, nullable=False, default=3)
    source = Column(Text, nullable=False)
    context_text = Column(Text)
    session_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("sentiment IN ('Positive', 'Negative', 'Neutral', 'Concern', 'DealBreaker')", name="preference_events_sentiment_check"),
        CheckConstraint("strength >= 1 AND strength <= 5", name="preference_events_strength_check"),
        CheckConstraint(
            "source IN ('UserStated', 'UserRating', 'SavedProperty', 'RejectedProperty', 'Comment', 'InspectionNote', 'AIInferred', 'ManualOverride')",
            name="preference_events_source_check",
        ),
    )


class DecisionJournalEntry(TimestampMixin, Base):
    __tablename__ = "decision_journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"))
    entry_type = Column(Text, nullable=False, default="note")
    title = Column(Text)
    body = Column(Text, nullable=False)
    body_tsvector = Column(TSVECTOR)
    mood = Column(Text)
    tags = Column(ARRAY(Text))
    is_pinned = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('note', 'reflection', 'decision', 'question', 'milestone', 'concern')",
            name="decision_journal_entry_type_check",
        ),
        CheckConstraint("mood IN ('excited', 'positive', 'neutral', 'uncertain', 'concerned')", name="decision_journal_mood_check"),
    )

    member_impacts = relationship("DecisionJournalMemberImpact", back_populates="entry", cascade="all, delete-orphan")


class DecisionJournalMemberImpact(Base):
    __tablename__ = "decision_journal_member_impacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(UUID(as_uuid=True), ForeignKey("decision_journal_entries.id", ondelete="CASCADE"), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    impact_note = Column(Text)
    sentiment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("sentiment IN ('positive', 'negative', 'neutral')", name="decision_journal_impact_sentiment_check"),
    )

    entry = relationship("DecisionJournalEntry", back_populates="member_impacts")
    member = relationship("FamilyMember")
