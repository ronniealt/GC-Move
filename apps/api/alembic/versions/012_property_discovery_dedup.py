"""012 property auto-discovery flags + per-family listing dedup

Revision ID: 012
Revises: 011
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("properties", sa.Column("auto_discovered", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("properties", sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True))

    op.drop_constraint("properties_status_check", "properties", type_="check")
    op.create_check_constraint(
        "properties_status_check",
        "properties",
        "status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', "
        "'sold', 'withdrawn', 'ingesting', 'evaluated', 'filtered', 'failed', 'duplicate')",
    )

    # Per-family dedup: the same family should never end up with two Property
    # rows for the same real-world listing, whether pasted manually twice or
    # re-surfaced by discovery. Scoped per-family (not global) so two different
    # families targeting the same suburb can each independently track the
    # same real listing.
    op.create_index(
        "ux_properties_family_source_listing",
        "properties",
        ["family_id", "source_platform", "source_listing_id"],
        unique=True,
        postgresql_where=sa.text("source_listing_id IS NOT NULL AND source_listing_id != '' AND deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ux_properties_family_source_listing", table_name="properties")
    op.drop_constraint("properties_status_check", "properties", type_="check")
    op.create_check_constraint(
        "properties_status_check",
        "properties",
        "status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', "
        "'sold', 'withdrawn', 'ingesting', 'evaluated', 'filtered', 'failed')",
    )
    op.drop_column("properties", "viewed_at")
    op.drop_column("properties", "auto_discovered")
