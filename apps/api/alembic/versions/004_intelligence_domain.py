"""004 intelligence domain — evaluations, recommendations, preferences, journal

Revision ID: 004
Revises: 003
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB, TSVECTOR

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("property_evaluations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id")),
        sa.Column("school_id", UUID(as_uuid=True), sa.ForeignKey("schools.id")),
        sa.Column("evaluation_version", sa.Text, nullable=False, server_default="v1"),
        sa.Column("openai_model", sa.Text, nullable=False, server_default="gpt-4o"),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("executive_summary", sa.Text),
        sa.Column("community_narrative", sa.Text),
        sa.Column("lifestyle_narrative", sa.Text),
        sa.Column("school_narrative", sa.Text),
        sa.Column("property_narrative", sa.Text),
        sa.Column("financial_narrative", sa.Text),
        sa.Column("five_year_narrative", sa.Text),
        sa.Column("deal_breakers_flagged", ARRAY(sa.Text)),
        sa.Column("prompt_tokens", sa.Integer),
        sa.Column("completion_tokens", sa.Integer),
        sa.Column("total_cost_usd", sa.Numeric(8, 4)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_property_evaluations_family", "property_evaluations", ["family_id", "evaluated_at"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_property_evaluations_current", "property_evaluations", ["family_id", "property_id"], postgresql_where=sa.text("is_current = TRUE AND deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_property_evaluations_updated_at BEFORE UPDATE ON property_evaluations FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE property_evaluations ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON property_evaluations USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("evaluation_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("evaluation_id", UUID(as_uuid=True), sa.ForeignKey("property_evaluations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("community_score", sa.Numeric(4, 2)),
        sa.Column("lifestyle_score", sa.Numeric(4, 2)),
        sa.Column("school_score", sa.Numeric(4, 2)),
        sa.Column("property_score", sa.Numeric(4, 2)),
        sa.Column("financial_score", sa.Numeric(4, 2)),
        sa.Column("risk_score", sa.Numeric(4, 2)),
        sa.Column("family_fit_score", sa.Numeric(5, 2)),
        sa.Column("five_year_fit_score", sa.Numeric(5, 2)),
        sa.Column("owner_occupier_score", sa.Numeric(4, 2)),
        sa.Column("family_density_score", sa.Numeric(4, 2)),
        sa.Column("educational_attainment_score", sa.Numeric(4, 2)),
        sa.Column("median_income_score", sa.Numeric(4, 2)),
        sa.Column("crime_score", sa.Numeric(4, 2)),
        sa.Column("community_engagement_score", sa.Numeric(4, 2)),
        sa.Column("burleigh_access_score", sa.Numeric(4, 2)),
        sa.Column("beach_access_score", sa.Numeric(4, 2)),
        sa.Column("wellness_score", sa.Numeric(4, 2)),
        sa.Column("cafe_dining_score", sa.Numeric(4, 2)),
        sa.Column("outdoor_recreation_score", sa.Numeric(4, 2)),
        sa.Column("shopping_score", sa.Numeric(4, 2)),
        sa.Column("wellbeing_score", sa.Numeric(4, 2)),
        sa.Column("parent_community_score", sa.Numeric(4, 2)),
        sa.Column("academic_outcomes_score", sa.Numeric(4, 2)),
        sa.Column("school_commute_score", sa.Numeric(4, 2)),
        sa.Column("extracurricular_score", sa.Numeric(4, 2)),
        sa.Column("school_pathway_score", sa.Numeric(4, 2)),
        sa.Column("modernity_score", sa.Numeric(4, 2)),
        sa.Column("design_quality_score", sa.Numeric(4, 2)),
        sa.Column("indoor_outdoor_flow_score", sa.Numeric(4, 2)),
        sa.Column("pool_quality_score", sa.Numeric(4, 2)),
        sa.Column("home_office_score", sa.Numeric(4, 2)),
        sa.Column("entertaining_space_score", sa.Numeric(4, 2)),
        sa.Column("privacy_score", sa.Numeric(4, 2)),
        sa.Column("block_utility_score", sa.Numeric(4, 2)),
        sa.Column("weights_snapshot", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_evaluation_scores_family_fit", "evaluation_scores", ["family_id", sa.text("family_fit_score DESC NULLS LAST")])
    op.execute("ALTER TABLE evaluation_scores ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON evaluation_scores USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("evaluation_per_member",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("evaluation_id", UUID(as_uuid=True), sa.ForeignKey("property_evaluations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("commentary", sa.Text, nullable=False),
        sa.Column("key_positives", ARRAY(sa.Text)),
        sa.Column("key_concerns", ARRAY(sa.Text)),
        sa.Column("fit_score", sa.Numeric(4, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("ALTER TABLE evaluation_per_member ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON evaluation_per_member USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evaluation_id", UUID(as_uuid=True), sa.ForeignKey("property_evaluations.id"), nullable=False),
        sa.Column("rank_position", sa.Integer),
        sa.Column("family_fit_score", sa.Numeric(5, 2)),
        sa.Column("previous_rank", sa.Integer),
        sa.Column("score_delta", sa.Numeric(5, 2)),
        sa.Column("status", sa.Text, nullable=False, server_default="active"),
        sa.Column("headline", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("ranked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("family_id", "property_id", name="recommendations_family_property_unique"),
        sa.CheckConstraint("status IN ('active', 'archived', 'dismissed', 'accepted')", name="recommendations_status_check"),
    )
    op.create_index("idx_recommendations_family_rank", "recommendations", ["family_id", "rank_position"], postgresql_where=sa.text("status = 'active'"))
    op.execute("CREATE UNIQUE INDEX idx_recommendations_family_property ON recommendations(family_id, property_id)")
    op.execute("CREATE TRIGGER trg_recommendations_updated_at BEFORE UPDATE ON recommendations FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON recommendations USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("recommendation_explanations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("recommendation_id", UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("dimension", sa.Text, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("score", sa.Numeric(4, 2)),
        sa.Column("supporting_data", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("dimension IN ('community', 'lifestyle', 'school', 'property', 'financial', 'family_fit', 'risk')", name="recommendation_explanations_dimension_check"),
    )
    op.execute("ALTER TABLE recommendation_explanations ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON recommendation_explanations USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("preference_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id")),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id")),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id")),
        sa.Column("school_id", UUID(as_uuid=True), sa.ForeignKey("schools.id")),
        sa.Column("attribute", sa.Text, nullable=False),
        sa.Column("sentiment", sa.Text, nullable=False),
        sa.Column("strength", sa.Integer, nullable=False, server_default="3"),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("context_text", sa.Text),
        sa.Column("session_id", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("sentiment IN ('Positive', 'Negative', 'Neutral', 'Concern', 'DealBreaker')", name="preference_events_sentiment_check"),
        sa.CheckConstraint("strength >= 1 AND strength <= 5", name="preference_events_strength_check"),
        sa.CheckConstraint("source IN ('UserStated', 'UserRating', 'SavedProperty', 'RejectedProperty', 'Comment', 'InspectionNote', 'AIInferred', 'ManualOverride')", name="preference_events_source_check"),
    )
    op.create_index("idx_preference_events_family_attribute", "preference_events", ["family_id", "attribute"])
    op.create_index("idx_preference_events_family_created", "preference_events", ["family_id", "created_at"])
    op.execute("ALTER TABLE preference_events ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON preference_events USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("decision_journal_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id")),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id")),
        sa.Column("entry_type", sa.Text, nullable=False, server_default="note"),
        sa.Column("title", sa.Text),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("body_tsvector", TSVECTOR, sa.Computed(
            "to_tsvector('english', COALESCE(title, '') || ' ' || body)", persisted=True
        )),
        sa.Column("mood", sa.Text),
        sa.Column("tags", ARRAY(sa.Text)),
        sa.Column("is_pinned", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("entry_type IN ('note', 'reflection', 'decision', 'question', 'milestone', 'concern')", name="decision_journal_entry_type_check"),
        sa.CheckConstraint("mood IN ('excited', 'positive', 'neutral', 'uncertain', 'concerned')", name="decision_journal_mood_check"),
    )
    op.execute("CREATE INDEX idx_decision_journal_fts ON decision_journal_entries USING GIN(body_tsvector) WHERE deleted_at IS NULL")
    op.create_index("idx_decision_journal_family_created", "decision_journal_entries", ["family_id", "created_at"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_decision_journal_entries_updated_at BEFORE UPDATE ON decision_journal_entries FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE decision_journal_entries ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON decision_journal_entries USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("decision_journal_member_impacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entry_id", UUID(as_uuid=True), sa.ForeignKey("decision_journal_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("impact_note", sa.Text),
        sa.Column("sentiment", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("sentiment IN ('positive', 'negative', 'neutral')", name="decision_journal_impact_sentiment_check"),
    )
    op.execute("ALTER TABLE decision_journal_member_impacts ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON decision_journal_member_impacts USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")


def downgrade() -> None:
    op.drop_table("decision_journal_member_impacts")
    op.drop_table("decision_journal_entries")
    op.drop_table("preference_events")
    op.drop_table("recommendation_explanations")
    op.drop_table("recommendations")
    op.drop_table("evaluation_per_member")
    op.drop_table("evaluation_scores")
    op.drop_table("property_evaluations")
