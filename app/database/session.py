"""
Database Session

Provides SQLAlchemy session management for AI Career Assistant.

Every repository should obtain database sessions from this module
instead of creating them directly.
"""

from sqlalchemy.orm import sessionmaker

from app.database.engine import engine

# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)