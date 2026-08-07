"""
Company Model

Represents a company that hires candidates.

A company can have multiple jobs and job postings across
different job platforms.
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Company(BaseModel):
    """
    Represents a hiring company.
    """

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    careers_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    headquarters: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    jobs: Mapped[list["Job"]] = relationship(
    	back_populates="company",
    	cascade="all, delete-orphan",
    )