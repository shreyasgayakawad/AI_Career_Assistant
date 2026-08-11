"""
Google OAuth Service

Creates authorization URLs for the Google OpenID Connect login flow.
"""

from sqlalchemy.orm import Session

from app.config.settings import GOOGLE_CLIENT_ID
from app.connectors.google_oauth import build_authorization_url
from app.connectors.google_token_client import GoogleTokenClient
from app.models.user import User
from app.services.google_identity_service import GoogleIdentityService
from app.services.google_login_state_service import (
    GoogleLoginStateService,
)


class GoogleOAuthService:
    """
    Start Google OpenID Connect authorization for sign-in.
    """

    def __init__(self, session: Session):
        self.google_login_state_service = (
            GoogleLoginStateService(session)
        )
        self.google_identity_service = GoogleIdentityService(session)
        self.token_client = GoogleTokenClient()

    def create_authorization_url(self) -> str:
        """
        Create login state and build the Google authorization URL.
        """

        if not GOOGLE_CLIENT_ID:
            raise ValueError(
                "GOOGLE_CLIENT_ID is not configured."
            )

        google_login_state = (
            self.google_login_state_service.create_state()
        )

        return build_authorization_url(
            state=google_login_state.state,
        )

    def handle_callback(
        self,
        *,
        state: str,
        code: str | None = None,
        error: str | None = None,
        error_description: str | None = None,
    ) -> User:
        """
        Validate a Google callback and resolve the existing user.
        """

        self.google_login_state_service.consume_state(state)

        if error:
            detail = "Google authorization failed."

            if error_description:
                detail = f"{detail} {error_description}"

            raise ValueError(detail)

        if not code:
            raise ValueError("Google authorization code is missing.")

        token_data = self.token_client.exchange_code(code)
        identity = self.token_client.verify_identity(
            token_data["id_token"],
        )

        return self.google_identity_service.resolve_existing_user(
            google_subject=identity["sub"],
            email=identity["email"],
            email_verified=identity["email_verified"],
        )
