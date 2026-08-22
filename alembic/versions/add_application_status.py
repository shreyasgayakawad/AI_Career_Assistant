"""Add status column to applications table

Revision ID: add_application_status
Revises: add_salary_min_max_columns
Create Date: 2026-08-20 20:40:12.835555
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_application_status"
down_revision = "add_salary_min_max_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add status column to applications table."""
    op.add_column(
        "applications",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="APPLIED",
        ),
    )


def downgrade() -> None:
    """Remove status column from applications table."""
    op.drop_column("applications", "status")