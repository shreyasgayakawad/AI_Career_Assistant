"""
Base Model

Provides common fields shared by all database models.

Every ORM model in AI Career Assistant should inherit from
BaseModel instead of Base.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BaseModel(Base):
    """
    Base class for all ORM models.

    Includes:
    - Primary key
    - Creation timestamp
    - Last updated timestamp
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )