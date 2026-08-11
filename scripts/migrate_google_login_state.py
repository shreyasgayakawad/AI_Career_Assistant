"""
Google Login State Schema Migration

Creates the table used for temporary Google login authorization state.
"""

from app.database.engine import engine
from app.models.google_login_state import GoogleLoginState


def migrate() -> None:
    """
    Create the Google login state table when it is missing.
    """

    GoogleLoginState.__table__.create(
        bind=engine,
        checkfirst=True,
    )


if __name__ == "__main__":
    migrate()
    print("Google login state schema migration completed.")
