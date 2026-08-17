"""Add candidate skill, work experience, and education tables

Revision ID: 1b7d079adb9f
Revises: 35b0078a1016
Create Date: 2026-08-17 01:36:10.931496
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b7d079adb9f'
down_revision: Union[str, Sequence[str], None] = '35b0078a1016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'candidate_skills',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('candidate_profile_id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('created_at', sa.DATETIME(), nullable=False),
        sa.Column('updated_at', sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_profile_id'], ['candidate_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'candidate_work_experiences',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('candidate_profile_id', sa.INTEGER(), nullable=False),
        sa.Column('company_name', sa.VARCHAR(length=200), nullable=False),
        sa.Column('job_title', sa.VARCHAR(length=100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=False),
        sa.Column('updated_at', sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_profile_id'], ['candidate_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'candidate_educations',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('candidate_profile_id', sa.INTEGER(), nullable=False),
        sa.Column('institution', sa.VARCHAR(length=200), nullable=False),
        sa.Column('degree', sa.VARCHAR(length=100), nullable=False),
        sa.Column('field_of_study', sa.VARCHAR(length=100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=False),
        sa.Column('updated_at', sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_profile_id'], ['candidate_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table('candidate_educations')
    op.drop_table('candidate_work_experiences')
    op.drop_table('candidate_skills')