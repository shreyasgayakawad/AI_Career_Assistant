"""
Application Model

Represents a user's application to a specific job posting.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Application(BaseModel):
    """
    Represents an application submitted for a specific job posting.
    """

    __tablename__ = "applications"

    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id"),
        nullable=False,
        unique=True,
    )

    resume_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    job_posting: Mapped["JobPosting"] = relationship(
        back_populates="application",
    )