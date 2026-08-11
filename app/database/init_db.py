"""
Database Initialization

Creates all database tables defined by SQLAlchemy ORM models.
"""

from app.database.base import Base
from app.database.engine import engine

# Import all models so SQLAlchemy registers them.

from app.models.application import Application  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.google_login_state import (  # noqa: F401
    GoogleLoginState,
)
from app.models.job import Job  # noqa: F401
from app.models.job_posting import JobPosting  # noqa: F401
from app.models.portal_connection import PortalConnection  # noqa: F401
from app.models.source import Source  # noqa: F401
from app.models.user import User  # noqa: F401


def initialize_database() -> None:
    """
    Create all database tables.
    """

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
