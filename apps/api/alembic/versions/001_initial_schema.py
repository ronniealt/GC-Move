"""001 initial schema — family domain

Revision ID: 001
Revises:
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.create_table("families",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("primary_suburb_target", sa.Text),
        sa.Column("budget_min_aud", sa.Integer),
        sa.Column("budget_max_aud", sa.Integer),
        sa.Column("target_move_date", sa.Date),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("onboarding_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("scoring_model_version", sa.Text, nullable=False, server_default="v1"),
        sa.Column("weight_community", sa.Numeric(4, 3), nullable=False, server_default="0.250"),
        sa.Column("weight_lifestyle", sa.Numeric(4, 3), nullable=False, server_default="0.200"),
        sa.Column("weight_school", sa.Numeric(4, 3), nullable=False, server_default="0.200"),
        sa.Column("weight_property", sa.Numeric(4, 3), nullable=False, server_default="0.200"),
        sa.Column("weight_financial", sa.Numeric(4, 3), nullable=False, server_default="0.150"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "ABS((weight_community + weight_lifestyle + weight_school + weight_property + weight_financial) - 1.0) < 0.001",
            name="weights_sum_to_one"
        ),
    )
    op.execute("CREATE TRIGGER trg_families_updated_at BEFORE UPDATE ON families FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("family_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("first_name", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("age", sa.Integer),
        sa.Column("birth_year", sa.Integer),
        sa.Column("is_school_age", sa.Boolean, sa.Computed("age >= 4 AND age <= 18", persisted=True)),
        sa.Column("notes", sa.Text),
        sa.Column("avatar_emoji", sa.Text, server_default="👤"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("role IN ('primary_adult', 'secondary_adult', 'child', 'pet')", name="family_members_role_check"),
        sa.CheckConstraint("age >= 0 AND age <= 120", name="family_members_age_check"),
    )
    op.execute("CREATE TRIGGER trg_family_members_updated_at BEFORE UPDATE ON family_members FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE family_members ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON family_members USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("family_users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("clerk_user_id", sa.Text, nullable=False, unique=True),
        sa.Column("family_member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id", ondelete="SET NULL")),
        sa.Column("role", sa.Text, nullable=False, server_default="member"),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("role IN ('primary', 'member')", name="family_users_role_check"),
    )
    op.create_index("idx_family_users_clerk_user_id", "family_users", ["clerk_user_id"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_family_users_family_id", "family_users", ["family_id"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_family_users_updated_at BEFORE UPDATE ON family_users FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    op.create_table("family_invites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_by_user_id", UUID(as_uuid=True), sa.ForeignKey("family_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False, server_default="member"),
        sa.Column("invite_token", sa.Text, nullable=False, unique=True),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW() + INTERVAL '7 days'")),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("accepted_by_user_id", UUID(as_uuid=True), sa.ForeignKey("family_users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("role IN ('primary', 'member')", name="family_invites_role_check"),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'expired', 'revoked')", name="family_invites_status_check"),
    )
    op.create_index("idx_family_invites_token", "family_invites", ["invite_token"], postgresql_where=sa.text("status = 'pending'"))
    op.create_index("idx_family_invites_email", "family_invites", ["email", "status"])

    op.create_table("family_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("attribute", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("current_weight", sa.Numeric(3, 1), nullable=False, server_default="2.5"),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False, server_default="0.0"),
        sa.Column("status", sa.Text, nullable=False, server_default="Emerging"),
        sa.Column("positive_signal_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("negative_signal_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_signal_at", sa.DateTime(timezone=True)),
        sa.Column("is_deal_breaker", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deal_breaker_set_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('Emerging', 'Confirmed', 'Contradicted', 'Retired', 'Manual')", name="family_preferences_status_check"),
        sa.UniqueConstraint("family_id", "attribute", name="family_preferences_family_attribute_unique"),
    )
    op.create_index("idx_family_preferences_family_attribute", "family_preferences", ["family_id", "attribute"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_family_preferences_status", "family_preferences", ["family_id", "status"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_family_preferences_updated_at BEFORE UPDATE ON family_preferences FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE family_preferences ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON family_preferences USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("family_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("family_members.id")),
        sa.Column("memory_type", sa.Text, nullable=False),
        sa.Column("attribute", sa.Text),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("structured", JSONB),
        sa.Column("source", sa.Text),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False, server_default="1.0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("memory_type IN ('Permanent', 'Preference', 'Learned', 'Session', 'Decision')", name="family_memory_type_check"),
    )
    op.create_index("idx_family_memory_family_type", "family_memory", ["family_id", "memory_type"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.execute("CREATE TRIGGER trg_family_memory_updated_at BEFORE UPDATE ON family_memory FOR EACH ROW EXECUTE FUNCTION set_updated_at()")
    op.execute("ALTER TABLE family_memory ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON family_memory USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")

    op.create_table("memory_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("memory_id", UUID(as_uuid=True), sa.ForeignKey("family_memory.id")),
        sa.Column("preference_id", UUID(as_uuid=True), sa.ForeignKey("family_preferences.id")),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("attribute", sa.Text),
        sa.Column("old_value", JSONB),
        sa.Column("new_value", JSONB),
        sa.Column("triggered_by", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_memory_events_family", "memory_events", ["family_id", "created_at"])
    op.execute("ALTER TABLE memory_events ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY family_isolation ON memory_events USING (family_id = current_setting('app.current_family_id', TRUE)::UUID)")


def downgrade() -> None:
    op.drop_table("memory_events")
    op.drop_table("family_memory")
    op.drop_table("family_preferences")
    op.drop_table("family_invites")
    op.drop_table("family_users")
    op.drop_table("family_members")
    op.drop_table("families")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at CASCADE")
