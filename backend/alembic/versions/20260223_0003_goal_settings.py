"""add goal settings table

Revision ID: 20260223_0003
Revises: 20260223_0002
Create Date: 2026-02-23 18:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260223_0003"
down_revision = "20260223_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "goal_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal_weight_kg", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("id = 1", name="ck_goal_settings_singleton_id"),
    )


def downgrade() -> None:
    op.drop_table("goal_settings")
