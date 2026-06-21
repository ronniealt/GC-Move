"""005 operational domain — inspections, advisor, audit

Revision ID: 005
Revises: 004
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, INET, UUID, JSONB

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("inspections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("inspection_type", sa.Text, nullable=False, server_default="open_home"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.Text, nullable=False, server_default="scheduled"),
        sa.Column("overall_impression", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("street_feel", sa.Text),
        sa.Column("neighbour_observations", sa.Text),
        sa.Column("deal_breakers_found", ARRAY(sa.Text)),
        sa.Column("report_url", sa.Text),
        sa.Column("report_summary", sa.Text),
        sa.Column("pest_issues", sa.Boolean),
        sa.Column("structural_issues", sa.Boolean),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("inspection_type IN ('open_home', 'private', 'building_pest', 'virtual')", name="inspections_type_check"),
        sa.CheckConstraint("status IN ('scheduled', 'completed', 'cancelled', 'missed')", name="inspections_status_check"),
        sa.CheckConstraint("overall_impression IN ('love', 'like', 'neutral', 'dislike', 'reject')", name="inspections_impression_check"),
    )
    op.create_index("idx_inspections_family_status", "inspections", ["family_id", "status"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_inspections_updated_at BEFORE UPDATE ON inspections FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE inspections ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON inspections USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("ai_advisor_threads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("openai_thread_id", sa.Text, nullable=False, unique=True),
        sa.Column("thread_name", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_ai_advisor_threads_family", "ai_advisor_threads", ["family_id"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_ai_advisor_threads_updated_at BEFORE UPDATE ON ai_advisor_threads FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE ai_advisor_threads ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON ai_advisor_threads USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("ai_advisor_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("thread_id", UUID(as_uuid=True), sa.ForeignKey("ai_advisor_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("openai_message_id", sa.Text),
        sa.Column("property_id", UUID(as_uuid=True), sa.ForeignKey("properties.id")),
        sa.Column("tokens_used", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="ai_advisor_messages_role_check"),
    )
    op.create_index("idx_ai_advisor_messages_thread", "ai_advisor_messages", ["thread_id", "created_at"])
    op.execute("ALTER TABLE ai_advisor_messages ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON ai_advisor_messages USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("notification_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), nullable=False, unique=True),
        sa.Column("email_new_evaluation", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("email_rank_change", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("email_daily_digest", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("email_inspection_reminder", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("push_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("digest_time", sa.Time, server_default="07:00:00"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("CREATE TRIGGER trg_notification_settings_updated_at BEFORE UPDATE ON notification_settings FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("market_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id"), nullable=False),
        sa.Column("snapshot_date", sa.Date, nullable=False),
        sa.Column("median_house_price_aud", sa.Integer),
        sa.Column("median_unit_price_aud", sa.Integer),
        sa.Column("days_on_market_median", sa.Integer),
        sa.Column("clearance_rate_pct", sa.Numeric(5, 2)),
        sa.Column("price_growth_1yr_pct", sa.Numeric(6, 2)),
        sa.Column("price_growth_3yr_pct", sa.Numeric(6, 2)),
        sa.Column("price_growth_5yr_pct", sa.Numeric(6, 2)),
        sa.Column("rental_yield_pct", sa.Numeric(5, 2)),
        sa.Column("supply_demand_index", sa.Numeric(5, 2)),
        sa.Column("source", sa.Text, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("suburb_id", "snapshot_date", "source", name="market_snapshots_unique"),
        sa.CheckConstraint("source IN ('manual', 'proptrack', 'reiq', 'corelogic')", name="market_snapshots_source_check"),
    )
    op.create_index("idx_market_snapshots_suburb_date", "market_snapshots", ["suburb_id", "snapshot_date"])

    op.create_table("audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id")),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id")),
        sa.Column("actor_type", sa.Text, nullable=False),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("entity_type", sa.Text),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("old_state", JSONB),
        sa.Column("new_state", JSONB),
        sa.Column("ip_address", INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("session_id", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("actor_type IN ('user', 'system', 'ai', 'admin')", name="audit_log_actor_type_check"),
    )
    op.create_index("idx_audit_log_family", "audit_log", ["family_id", "created_at"])
    op.create_index("idx_audit_log_entity", "audit_log", ["entity_type", "entity_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("market_snapshots")
    op.drop_table("notification_settings")
    op.drop_table("ai_advisor_messages")
    op.drop_table("ai_advisor_threads")
    op.drop_table("inspections")
