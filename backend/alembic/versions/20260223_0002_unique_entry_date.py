"""add unique constraint for entry_date

Revision ID: 20260223_0002
Revises: 20260223_0001
Create Date: 2026-02-23 17:48:00
"""

from alembic import op


revision = "20260223_0002"
down_revision = "20260223_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # deterministic cleanup: keep latest id for duplicate day
    op.execute(
        """
        DELETE FROM weight_entries
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM weight_entries
            GROUP BY entry_date
        )
        """
    )
    op.create_index(
        "uq_weight_entries_entry_date",
        "weight_entries",
        ["entry_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_weight_entries_entry_date", table_name="weight_entries")
