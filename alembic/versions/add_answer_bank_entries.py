"""Add answer bank entries table

Revision ID: add_answer_bank_entries
Revises: add_application_status
Create Date: 2026-08-23 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_answer_bank_entries"
down_revision = "add_application_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add answer_bank_entries table."""
    op.create_table(
        "answer_bank_entries",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("question_text", sa.TEXT(), nullable=False),
        sa.Column("answer_text", sa.TEXT(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove answer_bank_entries table."""
    op.drop_table("answer_bank_entries")
