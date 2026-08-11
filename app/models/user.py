"""
User Model

Represents a user of the AI Career Assistant.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class User(BaseModel):
    """
    Represents a user of the application.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    google_subject: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    portal_connections: Mapped[list["PortalConnection"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )