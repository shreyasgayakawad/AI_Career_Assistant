"""
Candidate Skill Model

Represents an individual skill stored in a candidate's profile.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class CandidateSkill(BaseModel):
    """
    An individual skill belonging to a candidate profile.
    """

    __tablename__ = "candidate_skills"

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )