"""
API Dependencies

Shared FastAPI dependencies.
"""

from collections.abc import Generator

from app.database.session import SessionLocal


def get_db() -> Generator:
    """
    Provide a database session for each request.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()