"""
Google Login State Service

Creates and validates short-lived, single-use Google sign-in states.
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.google_login_state import GoogleLoginState
from app.repositories.google_login_state_repository import (
    GoogleLoginStateRepository,
)


class GoogleLoginStateService:
    """
    Manage authorization state for unauthenticated Google login.
    """

    STATE_EXPIRATION_MINUTES = 10

    def __init__(self, session: Session):
        self.google_login_state_repository = (
            GoogleLoginStateRepository(session)
        )

    def create_state(self) -> GoogleLoginState:
        """
        Create and persist a short-lived Google login state.
        """

        state_value = secrets.token_urlsafe(32)
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=self.STATE_EXPIRATION_MINUTES)
        ).replace(tzinfo=None)

        google_login_state = GoogleLoginState(
            state=state_value,
            expires_at=expires_at,
        )

        return self.google_login_state_repository.create(
            google_login_state,
        )

    def consume_state(self, state: str) -> GoogleLoginState:
        """
        Validate and atomically consume a Google login state.

        Raises ValueError when the state is missing, expired, or has
        already been consumed.
        """

        google_login_state = (
            self.google_login_state_repository.get_by_state(
                state,
            )
        )

        if google_login_state is None:
            raise ValueError("Invalid Google login state.")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if google_login_state.expires_at <= now:
            raise ValueError("Google login state has expired.")

        consumed = self.google_login_state_repository.consume(
            google_login_state,
        )

        if not consumed:
            raise ValueError("Invalid Google login state.")

        return google_login_state
