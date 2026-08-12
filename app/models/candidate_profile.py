"""
Candidate Profile Model

Represents the career profile belonging to an application user.
"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


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

    user: Mapped["User"] = relationship(
        back_populates="candidate_profile",
    )