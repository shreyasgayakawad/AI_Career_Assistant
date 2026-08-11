"""
Google Login State Model

Stores temporary state values for unauthenticated Google login
authorization requests.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class GoogleLoginState(BaseModel):
    """
    Represents a pending Google sign-in authorization request.
    """

    __tablename__ = "google_login_states"

    state: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
