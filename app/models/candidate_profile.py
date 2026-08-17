"""
Candidate Profile Model

Represents the career profile belonging to an application user.
"""

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

from app.models.candidate_skill import CandidateSkill
from app.models.candidate_education import CandidateEducation
from app.models.candidate_work_experience import CandidateWorkExperience


class CandidateProfile(BaseModel):
    """
    Represents a user's career and professional profile.
    """

    __tablename__ = "candidate_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    professional_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Structured relationships (new in Phase 4):
    # These provide ORM-level navigation from a profile to its structured entries.
    # The child models hold the foreign key; no back_populates is needed on
    # the profile side so as not to disturb the existing model registries.
    skills_list: Mapped[list["CandidateSkill"]] = relationship(
        cascade="all, delete-orphan",
    )
    work_experiences: Mapped[list["CandidateWorkExperience"]] = relationship(
        cascade="all, delete-orphan",
    )
    education_entries: Mapped[list["CandidateEducation"]] = relationship(
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship(
        back_populates="candidate_profile",
    )