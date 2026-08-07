"""
Database Initialization

Creates all database tables defined by SQLAlchemy ORM models.
"""

from app.database.base import Base
from app.database.engine import engine

# Import all models here so SQLAlchemy registers them.
from app.models.source import Source  # noqa: F401


def initialize_database() -> None:
    """
    Create all database tables.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")