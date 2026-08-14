"""
JobPosting Model

Represents a job posting discovered from a specific job source.

Multiple job postings may point to the same logical job.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class JobPosting(BaseModel):
    """
    Represents a scraped job posting.
    """

    __tablename__ = "job_postings"

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "external_job_id",
            name="uq_job_posting_source_external_id",
        ),
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"),
        nullable=False,
    )

    external_job_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    posting_url: Mapped[str] = mapped_column(
        String(1000),
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    work_mode: Mapped[str] = mapped_column(
        String(20),
        default="UNKNOWN",
        nullable=False,
    )

    salary: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    posted_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    job: Mapped["Job"] = relationship(
        back_populates="postings",
    )

    source: Mapped["Source"] = relationship(
        back_populates="postings",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job_posting",
        cascade="all, delete-orphan",
    )