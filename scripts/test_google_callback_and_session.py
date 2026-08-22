"""
Test Google Callback and Browser Session

Verifies a mocked Google callback links an existing user, issues a
browser cookie, and renders their authenticated career dashboard.
"""

from unittest.mock import patch

import app.models  # noqa: F401

from app.api.routes.google_oauth import google_callback
from app.api.routes.web import dashboard_page
from app.auth.jwt import decode_access_token
from app.config.settings import (
    AUTH_COOKIE_NAME,
    GOOGLE_LOGIN_SUCCESS_REDIRECT_URI,
)
from app.database.session import SessionLocal
from app.models.portal_connection import PortalConnection
from app.models.user import User
from app.services.google_login_state_service import (
    GoogleLoginStateService,
)


def main() -> None:
    """
    Test the Google callback and automatic browser session.
    """

    session = SessionLocal()
    user: User | None = None
    connection: PortalConnection | None = None
    state_value: str | None = None

    # Clean up any existing test user from previous runs
    existing_user = (
        session.query(User).filter(User.email == "google_callback_test@example.com").first()
    )
    if existing_user is not None:
        session.delete(existing_user)
        session.commit()

    try:
        user = User(
            name="Google Callback Test User",
            email="google_callback_test@example.com",
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        connection = PortalConnection(
            user_id=user.id,
            platform="LinkedIn",
            login_email=user.email,
            credential_reference="test-encrypted-credential",
            enabled=True,
            status="ACTIVE",
        )

        session.add(connection)
        session.commit()

        state = GoogleLoginStateService(
            session,
        ).create_state()

        state_value = state.state

        print("=" * 50)
        print("Google Callback and Browser Session Test")
        print("=" * 50)

        with (
            patch(
                "app.api.routes.google_oauth.GOOGLE_ENABLED",
                True,
            ),
            patch(
                "app.services.google_oauth_service"
                ".GoogleTokenClient.exchange_code",
                return_value={
                    "id_token": "test-id-token",
                },
            ),
            patch(
                "app.services.google_oauth_service"
                ".GoogleTokenClient.verify_identity",
                return_value={
                    "sub": "google-callback-test-subject",
                    "email": user.email,
                    "email_verified": True,
                },
            ),
        ):
            callback_response = google_callback(
                state=state_value,
                code="test-authorization-code",
                session=session,
            )

        if callback_response.status_code != 303:
            raise RuntimeError(
                "Google callback did not return a redirect."
            )

        if (
            callback_response.headers.get("location")
            != GOOGLE_LOGIN_SUCCESS_REDIRECT_URI
        ):
            raise RuntimeError(
                "Google callback used the wrong success redirect."
            )

        cookie_header = callback_response.headers.get(
            "set-cookie",
            "",
        )

        if AUTH_COOKIE_NAME not in cookie_header:
            raise RuntimeError(
                "Google callback did not set the session cookie."
            )

        if "HttpOnly" not in cookie_header:
            raise RuntimeError(
                "Google session cookie is not HTTP-only."
            )

        browser_access_token = (
            cookie_header
            .split(";", 1)[0]
            .split("=", 1)[1]
        )

        if decode_access_token(
            browser_access_token,
        ) != user.id:
            raise RuntimeError(
                "Google session cookie belongs to the wrong user."
            )

        session.refresh(user)

        if user.google_subject != (
            "google-callback-test-subject"
        ):
            raise RuntimeError(
                "Google callback did not link the user identity."
            )

        print("Callback Identity Link    : Passed")
        print("HTTP-only Session Cookie  : Passed")

        dashboard_response = dashboard_page(
            session=session,
            current_user=user,
        )

        dashboard_body = dashboard_response.body.decode(
            "utf-8",
        )

        if "Welcome, Google Callback Test User" not in (
            dashboard_body
        ):
            raise RuntimeError(
                "Dashboard did not show the authenticated user."
            )

        if "Available Jobs" not in dashboard_body:
            raise RuntimeError(
                "Dashboard did not show available jobs."
            )

        if "Search" not in dashboard_body:
            raise RuntimeError(
                "Dashboard did not show the job search control."
            )

        print("Browser Session Dashboard : Passed")
        print()
        print(
            "Google callback and browser session test passed."
        )

    finally:
        if state_value:
            state = (
                GoogleLoginStateService(
                    session,
                )
                .google_login_state_repository
                .get_by_state(state_value)
            )

            if state is not None:
                session.delete(state)

        if connection is not None:
            session.delete(connection)

        if user is not None:
            session.delete(user)

        session.commit()
        session.close()


if __name__ == "__main__":
    main()