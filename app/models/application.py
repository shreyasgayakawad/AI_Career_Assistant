"""
Application Model

Represents a user's application to a specific job posting.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Application(BaseModel):
    """
    Represents an application submitted by a user
    for a specific job posting.
    """

    __tablename__ = "applications"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id"),
        nullable=False,
    )

    resume_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="APPLIED",
    )

    ALLOWED_STATUSES = {
        "APPLIED",
        "INTERVIEW",
        "OFFER",
        "REJECTED",
        "WITHDRAWN",
    }

    user: Mapped["User"] = relationship(
        back_populates="applications",
    )

    job_posting: Mapped["JobPosting"] = relationship(
        back_populates="applications",
    )