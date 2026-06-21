"""003 property domain

Revision ID: 003
Revises: 002
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("properties",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id")),
        sa.Column("source_url", sa.Text),
        sa.Column("source_platform", sa.Text),
        sa.Column("source_listing_id", sa.Text),
        sa.Column("address_street", sa.Text, nullable=False),
        sa.Column("address_suburb", sa.Text, nullable=False),
        sa.Column("address_state", sa.Text, nullable=False, server_default="QLD"),
        sa.Column("address_postcode", sa.String(4), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6)),
        sa.Column("longitude", sa.Numeric(9, 6)),
        sa.Column("property_type", sa.Text, nullable=False),
        sa.Column("bedrooms", sa.Integer),
        sa.Column("bathrooms", sa.Numeric(3, 1)),
        sa.Column("car_spaces", sa.Integer),
        sa.Column("land_area_sqm", sa.Integer),
        sa.Column("house_area_sqm", sa.Integer),
        sa.Column("listing_price_aud", sa.Integer),
        sa.Column("price_range_low_aud", sa.Integer),
        sa.Column("price_range_high_aud", sa.Integer),
        sa.Column("price_is_range", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("description_text", sa.Text),
        sa.Column("description_tsvector", TSVECTOR, sa.Computed(
            "to_tsvector('english', COALESCE(description_text, ''))", persisted=True
        )),
        sa.Column("flood_risk_category", sa.Text, server_default="unknown"),
        sa.Column("flood_risk_source_date", sa.Date),
        sa.Column("agent_name", sa.Text),
        sa.Column("agency_name", sa.Text),
        sa.Column("data_quality_score", sa.Integer, nullable=False, server_default="50"),
        sa.Column("extraction_confidence", sa.Numeric(3, 2)),
        sa.Column("status", sa.Text, nullable=False, server_default="saved"),
        sa.Column("is_favourite", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("family_notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("property_type IN ('house', 'townhouse', 'unit', 'acreage', 'other')", name="properties_type_check"),
        sa.CheckConstraint("status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', 'sold', 'withdrawn')", name="properties_status_check"),
        sa.CheckConstraint("flood_risk_category IN ('high', 'medium', 'low', 'none', 'unknown')", name="properties_flood_risk_check"),
        sa.CheckConstraint("source_platform IN ('realestate', 'domain', 'manual', 'agent')", name="properties_platform_check"),
    )
    op.create_index("idx_properties_family_status", "properties", ["family_id", "status"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_properties_family_suburb", "properties", ["family_id", "suburb_id"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_properties_family_favourite", "properties", ["family_id", "is_favourite"], postgresql_where=sa.text("deleted_at IS NULL AND is_favourite = TRUE"))
    op.create_index("idx_properties_address", "properties", ["address_street", "address_postcode", "family_id"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE INDEX idx_properties_description_fts ON properties USING GIN(description_tsvector)")
    op.execute("CREATE TRIGGER trg_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE properties ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON properties USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("property_features",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.Text, nullable=False),
        sa.Column("feature_value", sa.Text, nullable=False),
        sa.Column("feature_type", sa.Text, nullable=False, server_default="boolean"),
        sa.Column("confidence", sa.Numeric(3, 2), server_default="1.0"),
        sa.Column("source", sa.Text, server_default="extracted"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("property_id", "feature_key", name="property_features_unique"),
        sa.CheckConstraint("feature_type IN ('boolean', 'text', 'numeric', 'enum')", name="property_features_type_check"),
        sa.CheckConstraint("source IN ('extracted', 'manual', 'inferred')", name="property_features_source_check"),
    )
    op.create_index("idx_property_features_key_value", "property_features", ["property_id", "feature_key", "feature_value"])
    op.execute("CREATE TRIGGER trg_property_features_updated_at BEFORE UPDATE ON property_features FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE property_features ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON property_features USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("property_images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.Text, nullable=False),
        sa.Column("image_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("image_type", sa.Text, server_default="listing"),
        sa.Column("caption", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("image_type IN ('listing', 'floorplan', 'streetview', 'inspection')", name="property_images_type_check"),
    )
    op.execute("ALTER TABLE property_images ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON property_images USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("property_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("old_value", sa.Text),
        sa.Column("new_value", sa.Text),
        sa.Column("event_date", sa.Date),
        sa.Column("notes", sa.Text),
        sa.Column("source", sa.Text, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "event_type IN ('status_change', 'price_change', 'listed', 'relisted', 'price_drop', 'sold', 'withdrawn', 'passed_in')",
            name="property_history_event_type_check",
        ),
    )
    op.execute("ALTER TABLE property_history ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON property_history USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")


def downgrade() -> None:
    op.drop_table("property_history")
    op.drop_table("property_images")
    op.drop_table("property_features")
    op.drop_table("properties")
