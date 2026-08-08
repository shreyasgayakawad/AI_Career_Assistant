"""
Portal Connection Model

Represents a user's connection to an external job platform.
"""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class PortalConnection(BaseModel):
    """
    Represents a user's connection to an external
    job platform such as LinkedIn, Naukri, or Indeed.
    """

    __tablename__ = "portal_connections"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    login_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    credential_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="portal_connections",
    )