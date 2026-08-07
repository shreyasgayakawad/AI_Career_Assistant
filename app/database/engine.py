"""
Database Engine

Creates the SQLAlchemy Engine used to communicate with the database.

This module is responsible only for creating the Engine.
Session management and table creation are handled separately.
"""

from pathlib import Path

from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# Database Location
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "jobs.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ---------------------------------------------------------------------------
# SQLAlchemy Engine
# ---------------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)