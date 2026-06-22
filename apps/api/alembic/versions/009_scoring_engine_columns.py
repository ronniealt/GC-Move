"""009 add scoring engine columns to property_evaluations

Revision ID: 009
Revises: 008
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "property_evaluations",
        sa.Column("recommendation_level", sa.Text(), nullable=True),
    )
    op.add_column(
        "property_evaluations",
        sa.Column("meets_non_negotiables", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "property_evaluations",
        sa.Column("action_plan", JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("property_evaluations", "action_plan")
    op.drop_column("property_evaluations", "meets_non_negotiables")
    op.drop_column("property_evaluations", "recommendation_level")
