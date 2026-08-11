"""
Test Google OAuth Authorization

Verifies the Google authorization URL and disabled login response.
"""

from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.google_oauth import authorize_google
from app.config.settings import (
    GOOGLE_REDIRECT_URI,
    GOOGLE_SCOPES,
)
from app.database.session import SessionLocal
from app.services.google_oauth_service import GoogleOAuthService


def main() -> None:
    """
    Test Google authorization URL creation and feature disablement.
    """

    session = SessionLocal()

    try:
        print("=" * 50)
        print("Google OAuth Authorization Test")
        print("=" * 50)

        with (
            patch(
                "app.services.google_oauth_service"
                ".GOOGLE_CLIENT_ID",
                "test-google-client-id",
            ),
            patch(
                "app.connectors.google_oauth.GOOGLE_CLIENT_ID",
                "test-google-client-id",
            ),
        ):
            service = GoogleOAuthService(session)
            authorization_url = service.create_authorization_url()

        parsed_url = urlparse(authorization_url)
        parameters = parse_qs(parsed_url.query)
        state = parameters.get("state", [None])[0]

        if parsed_url.scheme != "https":
            raise RuntimeError(
                "Google authorization URL must use HTTPS."
            )

        if parameters.get("response_type") != ["code"]:
            raise RuntimeError(
                "Google authorization flow must request a code."
            )

        if parameters.get("client_id") != [
            "test-google-client-id"
        ]:
            raise RuntimeError(
                "Google authorization URL used the wrong client ID."
            )

        if parameters.get("redirect_uri") != [GOOGLE_REDIRECT_URI]:
            raise RuntimeError(
                "Google authorization URL used the wrong redirect URI."
            )

        if parameters.get("scope") != [GOOGLE_SCOPES]:
            raise RuntimeError(
                "Google authorization URL used the wrong scopes."
            )

        if not state:
            raise RuntimeError(
                "Google authorization URL did not contain state."
            )

        service.google_login_state_service.consume_state(state)

        print("Authorization URL          : Passed")

        with patch(
            "app.api.routes.google_oauth.GOOGLE_ENABLED",
            False,
        ):
            try:
                authorize_google(session=session)

                raise RuntimeError(
                    "Disabled Google login returned a redirect."
                )

            except HTTPException as exc:
                if exc.status_code != 503:
                    raise RuntimeError(
                        "Disabled Google login returned the wrong "
                        "status code."
                    ) from exc

                if exc.detail != "Google login is disabled.":
                    raise RuntimeError(
                        "Disabled Google login returned the wrong "
                        "message."
                    ) from exc

        print("Disabled Login Rejected    : Passed")

        print()
        print("Google OAuth authorization test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()
