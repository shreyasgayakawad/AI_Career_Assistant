"""
Candidate Work Experience Model

Represents a single work experience entry in a candidate's profile.
"""

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class CandidateWorkExperience(BaseModel):
    """
    A single work experience entry belonging to a candidate profile.
    """

    __tablename__ = "candidate_work_experiences"

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=False,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    job_title: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    start_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )