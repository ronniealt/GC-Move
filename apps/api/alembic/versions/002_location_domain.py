"""002 location domain — suburbs, schools

Revision ID: 002
Revises: 001
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("suburbs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("postcode", sa.String(4), nullable=False),
        sa.Column("state", sa.String(3), nullable=False, server_default="QLD"),
        sa.Column("lga", sa.Text, server_default="Gold Coast City Council"),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("bounding_box", JSONB),
        sa.Column("tier", sa.String(1)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("abs_sa2_code", sa.Text),
        sa.Column("police_division", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("tier IN ('A', 'B', 'C')", name="suburbs_tier_check"),
    )
    op.execute("CREATE UNIQUE INDEX idx_suburbs_name ON suburbs(LOWER(name))")
    op.create_index("idx_suburbs_postcode", "suburbs", ["postcode"])
    op.execute("CREATE TRIGGER trg_suburbs_updated_at BEFORE UPDATE ON suburbs FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("suburb_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id"), nullable=False, unique=True),
        sa.Column("owner_occupier_rate", sa.Numeric(5, 2)),
        sa.Column("owner_occupier_score", sa.Numeric(4, 2)),
        sa.Column("family_density_pct", sa.Numeric(5, 2)),
        sa.Column("family_density_score", sa.Numeric(4, 2)),
        sa.Column("educational_attainment_pct", sa.Numeric(5, 2)),
        sa.Column("educational_attainment_score", sa.Numeric(4, 2)),
        sa.Column("median_weekly_household_income_aud", sa.Integer),
        sa.Column("median_income_score", sa.Numeric(4, 2)),
        sa.Column("crime_index", sa.Numeric(6, 2)),
        sa.Column("crime_score", sa.Numeric(4, 2)),
        sa.Column("community_engagement_score", sa.Numeric(4, 2)),
        sa.Column("community_score", sa.Numeric(4, 2)),
        sa.Column("abs_data_year", sa.Integer, server_default="2021"),
        sa.Column("crime_data_quarter", sa.Text),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("CREATE TRIGGER trg_suburb_metrics_updated_at BEFORE UPDATE ON suburb_metrics FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("suburb_lifestyle_assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id"), nullable=False, unique=True),
        sa.Column("cafe_restaurant_count", sa.Integer, server_default="0"),
        sa.Column("gym_fitness_count", sa.Integer, server_default="0"),
        sa.Column("pilates_yoga_count", sa.Integer, server_default="0"),
        sa.Column("park_reserve_count", sa.Integer, server_default="0"),
        sa.Column("shopping_centre_count", sa.Integer, server_default="0"),
        sa.Column("medical_gp_count", sa.Integer, server_default="0"),
        sa.Column("childcare_count", sa.Integer, server_default="0"),
        sa.Column("supermarket_count", sa.Integer, server_default="0"),
        sa.Column("burleigh_drive_minutes", sa.Numeric(5, 1)),
        sa.Column("burleigh_access_score", sa.Numeric(4, 2)),
        sa.Column("beach_access_minutes", sa.Numeric(5, 1)),
        sa.Column("beach_access_score", sa.Numeric(4, 2)),
        sa.Column("wellness_infrastructure_score", sa.Numeric(4, 2)),
        sa.Column("cafe_dining_score", sa.Numeric(4, 2)),
        sa.Column("outdoor_recreation_score", sa.Numeric(4, 2)),
        sa.Column("shopping_score", sa.Numeric(4, 2)),
        sa.Column("lifestyle_score", sa.Numeric(4, 2)),
        sa.Column("travel_to_broadbeach_min", sa.Numeric(5, 1)),
        sa.Column("travel_to_airport_min", sa.Numeric(5, 1)),
        sa.Column("travel_to_robina_hospital_min", sa.Numeric(5, 1)),
        sa.Column("osm_poi_counts", JSONB),
        sa.Column("google_poi_counts", JSONB),
        sa.Column("travel_times_fetched_at", sa.DateTime(timezone=True)),
        sa.Column("poi_counts_fetched_at", sa.DateTime(timezone=True)),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("CREATE TRIGGER trg_suburb_lifestyle_assets_updated_at BEFORE UPDATE ON suburb_lifestyle_assets FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("lifestyle_asset_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("key", sa.Text, nullable=False, unique=True),
        sa.Column("label", sa.Text, nullable=False),
        sa.Column("icon", sa.Text),
        sa.Column("google_type", sa.Text),
        sa.Column("osm_tag", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table("schools",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("school_type", sa.Text, nullable=False),
        sa.Column("sector", sa.Text, nullable=False),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id")),
        sa.Column("address_street", sa.Text),
        sa.Column("address_suburb", sa.Text, nullable=False),
        sa.Column("address_postcode", sa.String(4)),
        sa.Column("latitude", sa.Numeric(9, 6)),
        sa.Column("longitude", sa.Numeric(9, 6)),
        sa.Column("acara_school_id", sa.Text, unique=True),
        sa.Column("year_range", sa.Text),
        sa.Column("total_enrolments", sa.Integer),
        sa.Column("icsea", sa.Integer),
        sa.Column("website_url", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("school_type IN ('primary', 'secondary', 'combined', 'special')", name="schools_type_check"),
        sa.CheckConstraint("sector IN ('government', 'catholic', 'independent')", name="schools_sector_check"),
    )
    op.execute("CREATE TRIGGER trg_schools_updated_at BEFORE UPDATE ON schools FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("school_catchments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("school_id", UUID(as_uuid=True), sa.ForeignKey("schools.id"), nullable=False),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id"), nullable=False),
        sa.Column("catchment_type", sa.Text, nullable=False, server_default="primary"),
        sa.Column("is_guaranteed", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("school_id", "suburb_id", "catchment_type", name="school_catchments_unique"),
        sa.CheckConstraint("catchment_type IN ('primary', 'secondary', 'out_of_catchment_accepted')", name="school_catchments_type_check"),
    )
    op.create_index("idx_school_catchments_suburb", "school_catchments", ["suburb_id", "catchment_type"])
    op.create_index("idx_school_catchments_school", "school_catchments", ["school_id"])

    op.create_table("school_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("school_id", UUID(as_uuid=True), sa.ForeignKey("schools.id"), nullable=False, unique=True),
        sa.Column("naplan_reading_pct_above_nms", sa.Numeric(5, 2)),
        sa.Column("naplan_numeracy_pct_above_nms", sa.Numeric(5, 2)),
        sa.Column("naplan_writing_pct_above_nms", sa.Numeric(5, 2)),
        sa.Column("naplan_data_year", sa.Integer),
        sa.Column("wellbeing_score", sa.Numeric(4, 2)),
        sa.Column("parent_community_score", sa.Numeric(4, 2)),
        sa.Column("academic_outcomes_score", sa.Numeric(4, 2)),
        sa.Column("commute_score", sa.Numeric(4, 2)),
        sa.Column("extracurricular_score", sa.Numeric(4, 2)),
        sa.Column("pathway_score", sa.Numeric(4, 2)),
        sa.Column("school_score", sa.Numeric(4, 2)),
        sa.Column("attendance_rate_pct", sa.Numeric(5, 2)),
        sa.Column("staff_to_student_ratio", sa.Numeric(5, 2)),
        sa.Column("annual_fee_aud", sa.Integer),
        sa.Column("has_boarding", sa.Boolean, server_default="false"),
        sa.Column("extracurricular_notes", sa.Text),
        sa.Column("data_year", sa.Integer),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("CREATE TRIGGER trg_school_metrics_updated_at BEFORE UPDATE ON school_metrics FOR EACH ROW EXECUTE FUNCTION set_updated_at()")


def downgrade() -> None:
    op.drop_table("school_metrics")
    op.drop_table("school_catchments")
    op.drop_table("schools")
    op.drop_table("lifestyle_asset_categories")
    op.drop_table("suburb_lifestyle_assets")
    op.drop_table("suburb_metrics")
    op.drop_table("suburbs")
