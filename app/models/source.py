"""
Source Model

Represents a platform where job postings are discovered.

Examples:
- LinkedIn
- Indeed
- Wellfound
- Greenhouse
- Lever
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Source(BaseModel):
    """
    Represents a job source/platform.
    """

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    base_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    scraper_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    postings: Mapped[list["JobPosting"]] = relationship(
    	back_populates="source",
    	cascade="all, delete-orphan",
    )