"""010 add deleted_at to tables missing it

Revision ID: 010
Revises: 009
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None

# Tables that use TimestampMixin in the model but were created without deleted_at
TABLES = [
    "suburbs",
    "suburb_metrics",
    "suburb_lifestyle_assets",
    "schools",
    "school_metrics",
    "notification_settings",
    "recommendations",
]


def upgrade() -> None:
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, "deleted_at")
