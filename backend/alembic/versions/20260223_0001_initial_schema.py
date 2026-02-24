"""initial schema

Revision ID: 20260223_0001
Revises:
Create Date: 2026-02-23 17:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260223_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weight_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entry_date", sa.Text(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("weight_entries")
