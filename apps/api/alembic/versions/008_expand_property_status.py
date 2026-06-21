"""008 expand property status for ingestion pipeline

Revision ID: 008
Revises: 007
Create Date: 2026-06-21
"""
from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("properties_status_check", "properties", type_="check")
    op.create_check_constraint(
        "properties_status_check",
        "properties",
        "status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', "
        "'sold', 'withdrawn', 'ingesting', 'evaluated', 'filtered', 'failed')",
    )


def downgrade() -> None:
    op.drop_constraint("properties_status_check", "properties", type_="check")
    op.create_check_constraint(
        "properties_status_check",
        "properties",
        "status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', 'sold', 'withdrawn')",
    )
