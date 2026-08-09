"""
OAuth State Service

Provides business logic for creating and validating OAuth
authorization state values.
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.oauth_state import OAuthState
from app.repositories.oauth_state_repository import (
    OAuthStateRepository,
)


class OAuthStateService:
    """
    Business service for OAuth authorization state.
    """

    STATE_EXPIRATION_MINUTES = 10

    def __init__(
        self,
        session: Session,
    ):
        self.oauth_state_repository = (
            OAuthStateRepository(session)
        )

    def create_state(
        self,
        user_id: int,
        platform: str,
    ) -> OAuthState:
        """
        Create a new OAuth authorization state.
        """

        state_value = secrets.token_urlsafe(32)

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=self.STATE_EXPIRATION_MINUTES,
            )
        ).replace(
            tzinfo=None,
        )

        oauth_state = OAuthState(
            user_id=user_id,
            platform=platform,
            state=state_value,
            expires_at=expires_at,
        )

        return self.oauth_state_repository.create(
            oauth_state,
        )

    def get_state(
        self,
        state: str,
    ) -> OAuthState | None:
        """
        Retrieve an OAuth state by its value.
        """

        return self.oauth_state_repository.get_by_state(
            state=state,
        )

    def validate_state(
        self,
        state: str,
        user_id: int,
        platform: str,
    ) -> OAuthState:
        """
        Validate an OAuth state against the authenticated user,
        platform, and expiration time.

        Raises ValueError when validation fails.
        """

        oauth_state = self.get_state(
            state=state,
        )

        if oauth_state is None:
            raise ValueError(
                "Invalid OAuth state."
            )

        if oauth_state.user_id != user_id:
            raise ValueError(
                "OAuth state does not belong to the user."
            )

        if oauth_state.platform != platform:
            raise ValueError(
                "OAuth state platform mismatch."
            )

        now = datetime.now(
            timezone.utc,
        ).replace(
            tzinfo=None,
        )

        if oauth_state.expires_at <= now:
            raise ValueError(
                "OAuth state has expired."
            )

        return oauth_state

    def consume_state(
        self,
        state: str,
        user_id: int,
        platform: str,
    ) -> OAuthState:
        """
        Validate and atomically consume an OAuth state.

        A successfully validated state is deleted immediately,
        preventing it from being reused.
        """

        oauth_state = self.validate_state(
            state=state,
            user_id=user_id,
            platform=platform,
        )

        consumed = self.oauth_state_repository.consume(
            oauth_state,
        )

        if not consumed:
            raise ValueError(
                "Invalid OAuth state."
            )

        return oauth_state