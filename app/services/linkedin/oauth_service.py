"""
LinkedIn OAuth Service

Provides business logic for the LinkedIn OAuth authorization
and callback flow.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.settings import LINKEDIN_SCOPES
from app.connectors.linkedin_oauth import build_authorization_url
from app.connectors.linkedin_token_client import (
    LinkedInTokenClient,
)
from app.models.portal_connection import PortalConnection
from app.services.oauth_state_service import OAuthStateService
from app.services.portal_connection_service import (
    PortalConnectionService,
)


class LinkedInOAuthService:
    """
    Business service for LinkedIn OAuth authorization.
    """

    def __init__(
        self,
        session: Session,
    ):
        self.oauth_state_service = OAuthStateService(
            session,
        )
        self.token_client = LinkedInTokenClient()
        self.portal_connection_service = (
            PortalConnectionService(session)
        )

    def create_authorization_url(
        self,
        user_id: int,
    ) -> str:
        """
        Create and persist OAuth state, then build the
        LinkedIn authorization URL.
        """

        oauth_state = self.oauth_state_service.create_state(
            user_id=user_id,
            platform="LinkedIn",
        )

        return build_authorization_url(
            state=oauth_state.state,
        )

    def handle_callback(
        self,
        state: str,
        code: str | None = None,
        error: str | None = None,
        error_description: str | None = None,
    ) -> tuple[PortalConnection, dict]:
        """
        Process a LinkedIn OAuth callback.

        The OAuth state is validated and consumed before
        processing the authorization result.

        Returns the created or updated portal connection
        and the LinkedIn UserInfo response.

        Raises ValueError for invalid OAuth state, OAuth
        authorization errors, token exchange failures,
        or invalid LinkedIn responses.
        """

        oauth_state = self.oauth_state_service.get_state(
            state=state,
        )

        if oauth_state is None:
            raise ValueError(
                "Invalid OAuth state."
            )

        self.oauth_state_service.consume_state(
            state=state,
            user_id=oauth_state.user_id,
            platform="LinkedIn",
        )

        if error:
            detail = "LinkedIn authorization failed."

            if error_description:
                detail = (
                    f"{detail} {error_description}"
                )

            raise ValueError(
                detail,
            )

        if not code:
            raise ValueError(
                "LinkedIn authorization code is missing."
            )

        token_data = self.token_client.exchange_code(
            code=code,
        )

        access_token = token_data.get(
            "access_token",
        )

        if not access_token:
            raise ValueError(
                "LinkedIn token response did not contain "
                "an access token."
            )

        userinfo = self.token_client.get_userinfo(
            access_token=access_token,
        )

        token_expires_at = self._get_token_expiration(
            token_data,
        )

        scopes = token_data.get(
            "scope",
        ) or LINKEDIN_SCOPES

        connection = (
            self.portal_connection_service
            .create_oauth_connection(
                user_id=oauth_state.user_id,
                platform="LinkedIn",
                login_email=userinfo.get("email", ""),
                external_user_id=str(
                    userinfo["sub"],
                ),
                oauth_scopes=str(scopes),
                access_token=access_token,
                token_expires_at=token_expires_at,
            )
        )

        return connection, userinfo

    @staticmethod
    def _get_token_expiration(
        token_data: dict,
    ) -> datetime | None:
        """
        Calculate the access-token expiration timestamp.
        """

        expires_in = token_data.get(
            "expires_in",
        )

        if expires_in is None:
            return None

        try:
            return (
                datetime.now(timezone.utc)
                + timedelta(
                    seconds=int(expires_in),
                )
            ).replace(
                tzinfo=None,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "LinkedIn token expiration was invalid."
            ) from exc