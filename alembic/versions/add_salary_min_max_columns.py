"""Add salary_min and salary_max columns to job_postings

Revision ID: add_salary_min_max_columns
Revises: 1b7d079adb9f
Create Date: 2026-08-18 15:14:36.835555
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_salary_min_max_columns"
down_revision = "1b7d079adb9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add salary_min and salary_max columns to job_postings table."""
    op.add_column(
        "job_postings",
        sa.Column("salary_min", sa.Integer(), nullable=True),
    )
    op.add_column(
        "job_postings",
        sa.Column("salary_max", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Remove salary_min and salary_max columns from job_postings table."""
    op.drop_column("job_postings", "salary_max")
    op.drop_column("job_postings", "salary_min")