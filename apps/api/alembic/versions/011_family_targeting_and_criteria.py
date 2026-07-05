"""011 family suburb targeting + structured non-negotiables

Revision ID: 011
Revises: 010
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("families", sa.Column("target_move_timeline", sa.Text(), nullable=True))

    op.create_table(
        "family_suburbs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("suburb_id", UUID(as_uuid=True), sa.ForeignKey("suburbs.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ux_family_suburbs_active",
        "family_suburbs",
        ["family_id", "suburb_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "family_non_negotiables",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("criterion_key", sa.Text(), nullable=False),
        sa.Column("comparator", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False, server_default="onboarding"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("comparator IN ('eq', 'gte', 'lte', 'has')", name="family_non_negotiables_comparator_check"),
        sa.CheckConstraint("source IN ('onboarding', 'settings', 'manual')", name="family_non_negotiables_source_check"),
    )
    op.create_index(
        "ux_family_non_negotiables_active",
        "family_non_negotiables",
        ["family_id", "criterion_key"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Backfill: preserve today's hardcoded non_negotiables.py behavior for any
    # family that existed before this migration, so scoring doesn't silently
    # change the moment the code switches to reading this table.
    op.get_bind().exec_driver_sql("""
    INSERT INTO family_non_negotiables (id, family_id, criterion_key, comparator, value, label, source)
    SELECT gen_random_uuid(), id, 'property_type', 'eq', 'house', 'House', 'manual' FROM families
    """)
    op.get_bind().exec_driver_sql("""
    INSERT INTO family_non_negotiables (id, family_id, criterion_key, comparator, value, label, source)
    SELECT gen_random_uuid(), id, 'has_pool', 'has', 'true', 'Pool', 'manual' FROM families
    """)
    op.get_bind().exec_driver_sql("""
    INSERT INTO family_non_negotiables (id, family_id, criterion_key, comparator, value, label, source)
    SELECT gen_random_uuid(), id, 'max_beach_drive_minutes', 'lte', '20', 'Beach < 20 min', 'manual' FROM families
    """)
    op.get_bind().exec_driver_sql("""
    INSERT INTO family_non_negotiables (id, family_id, criterion_key, comparator, value, label, source)
    SELECT gen_random_uuid(), id, 'max_burleigh_drive_minutes', 'lte', '20', 'Burleigh < 20 min', 'manual' FROM families
    """)


def downgrade() -> None:
    op.drop_index("ux_family_non_negotiables_active", table_name="family_non_negotiables")
    op.drop_table("family_non_negotiables")
    op.drop_index("ux_family_suburbs_active", table_name="family_suburbs")
    op.drop_table("family_suburbs")
    op.drop_column("families", "target_move_timeline")
