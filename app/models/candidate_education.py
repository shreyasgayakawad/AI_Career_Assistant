"""
Candidate Education Model

Represents a single education entry in a candidate's profile.
"""

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class CandidateEducation(BaseModel):
    """
    A single education entry belonging to a candidate profile.
    """

    __tablename__ = "candidate_educations"

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=False,
    )

    institution: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    degree: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    field_of_study: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    start_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )