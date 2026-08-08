"""
Portal Connection API Test

Tests authenticated portal connection API behavior.
"""

from datetime import datetime, timedelta, timezone

import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.portal_connections import (
    CreatePortalConnectionRequest,
    create_portal_connection,
    get_portal_connections,
)
from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.models.portal_connection import PortalConnection
from app.models.user import User


def main() -> None:
    """
    Test portal connection API behavior.
    """

    session = SessionLocal()

    try:
        user_email = "portal_api_test@example.com"
        second_user_email = (
            "portal_api_second_user@example.com"
        )

        # ---------------------------------------------------------
        # Clean up previous test users.
        # ---------------------------------------------------------

        existing_user = (
            session.query(User)
            .filter(User.email == user_email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)

        existing_second_user = (
            session.query(User)
            .filter(User.email == second_user_email)
            .first()
        )

        if existing_second_user:
            session.delete(existing_second_user)

        session.commit()

        # ---------------------------------------------------------
        # Create primary test user.
        # ---------------------------------------------------------

        user = User(
            name="Portal API Test User",
            email=user_email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # ---------------------------------------------------------
        # Create authentication token.
        # ---------------------------------------------------------

        token = create_access_token(
            user_id=user.id,
        )

        if not token:
            raise RuntimeError(
                "Authentication token was not created."
            )

        print()
        print("# Portal Connection API Test")
        print()

        # ---------------------------------------------------------
        # 1. Create LinkedIn connection.
        # ---------------------------------------------------------

        create_response = create_portal_connection(
            request=CreatePortalConnectionRequest(
                platform="LinkedIn",
                login_email=user.email,
            ),
            session=session,
            current_user=user,
        )

        print(
            f"Connection ID : {create_response.id}"
        )
        print(
            f"Platform      : {create_response.platform}"
        )
        print(
            f"Login Email   : {create_response.login_email}"
        )

        if create_response.platform != "LinkedIn":
            raise RuntimeError(
                "Incorrect platform returned."
            )

        if create_response.login_email != user.email:
            raise RuntimeError(
                "Incorrect login email returned."
            )

        if create_response.enabled is not True:
            raise RuntimeError(
                "New connection should be enabled."
            )

        if create_response.status != "ACTIVE":
            raise RuntimeError(
                "New connection should be ACTIVE."
            )

        print()
        print("Connection Creation : Passed")

        # ---------------------------------------------------------
        # 2. Add OAuth metadata directly to the database.
        #
        # In the real OAuth flow, these values will be produced
        # by the OAuth callback rather than by the API client.
        # ---------------------------------------------------------

        connection = (
            session.query(PortalConnection)
            .filter(
                PortalConnection.id
                == create_response.id,
            )
            .first()
        )

        if connection is None:
            raise RuntimeError(
                "Created portal connection was not found."
            )

        token_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=1)
        ).replace(tzinfo=None)

        connection.external_user_id = (
            "linkedin-member-api-123"
        )

        connection.oauth_scopes = (
            "openid profile email"
        )

        connection.credential_reference = (
            "secret-credential-reference"
        )

        connection.token_expires_at = (
            token_expires_at
        )

        session.commit()
        session.refresh(connection)

        print(
            "OAuth Metadata Setup : Passed"
        )

        # ---------------------------------------------------------
        # 3. Retrieve connections.
        # ---------------------------------------------------------

        connections = get_portal_connections(
            session=session,
            current_user=user,
        )

        if len(connections) != 1:
            raise RuntimeError(
                "Expected exactly one portal connection."
            )

        retrieved_response = connections[0]

        if retrieved_response.id != create_response.id:
            raise RuntimeError(
                "Retrieved connection ID does not match."
            )

        if (
            retrieved_response.external_user_id
            != "linkedin-member-api-123"
        ):
            raise RuntimeError(
                "External user ID was not returned correctly."
            )

        if (
            retrieved_response.oauth_scopes
            != "openid profile email"
        ):
            raise RuntimeError(
                "OAuth scopes were not returned correctly."
            )

        if (
            retrieved_response.token_expires_at
            != token_expires_at.isoformat()
        ):
            raise RuntimeError(
                "Token expiration was not returned correctly."
            )

        print(
            "Connection Retrieval : Passed"
        )

        print(
            "OAuth Metadata Response : Passed"
        )

        # ---------------------------------------------------------
        # 4. Verify credential reference is not exposed.
        # ---------------------------------------------------------

        response_fields = (
            retrieved_response.model_dump()
        )

        if "credential_reference" in response_fields:
            raise RuntimeError(
                "Credential reference must not be exposed "
                "by the API response."
            )

        print(
            "Credential Protection : Passed"
        )

        # ---------------------------------------------------------
        # 5. Duplicate connection prevention.
        # ---------------------------------------------------------

        try:
            create_portal_connection(
                request=CreatePortalConnectionRequest(
                    platform="LinkedIn",
                    login_email=user.email,
                ),
                session=session,
                current_user=user,
            )

            raise RuntimeError(
                "Duplicate LinkedIn connection was created."
            )

        except HTTPException as exc:
            if exc.status_code != 409:
                raise RuntimeError(
                    "Expected HTTP 409 for duplicate "
                    f"connection, got {exc.status_code}."
                )

        print(
            "Duplicate Prevention : Passed"
        )

        # ---------------------------------------------------------
        # 6. Create supported platforms.
        # ---------------------------------------------------------

        naukri_response = create_portal_connection(
            request=CreatePortalConnectionRequest(
                platform="Naukri",
                login_email=user.email,
            ),
            session=session,
            current_user=user,
        )

        if naukri_response.platform != "Naukri":
            raise RuntimeError(
                "Naukri connection was not created correctly."
            )

        surelyremote_response = create_portal_connection(
            request=CreatePortalConnectionRequest(
                platform="SurelyRemote",
                login_email=user.email,
            ),
            session=session,
            current_user=user,
        )

        if surelyremote_response.platform != "SurelyRemote":
            raise RuntimeError(
                "SurelyRemote connection was not created correctly."
            )

        print(
            "Multiple Platforms   : Passed"
        )

        # ---------------------------------------------------------
        # 7. Unsupported platform rejection.
        # ---------------------------------------------------------

        try:
            create_portal_connection(
                request=CreatePortalConnectionRequest(
                    platform="Remotely",
                    login_email=user.email,
                ),
                session=session,
                current_user=user,
            )

            raise RuntimeError(
                "Unsupported platform was accepted."
            )

        except HTTPException as exc:
            if exc.status_code != 409:
                raise RuntimeError(
                    "Expected HTTP 409 for unsupported "
                    f"platform, got {exc.status_code}."
                )

            if exc.detail != (
                "Unsupported job platform: Remotely."
            ):
                raise RuntimeError(
                    "Unexpected unsupported-platform error: "
                    f"{exc.detail}"
                )

        print(
            "Unsupported Platform  : Passed"
        )

        # ---------------------------------------------------------
        # 8. Create second user.
        # ---------------------------------------------------------

        second_user = User(
            name="Second Portal API User",
            email=second_user_email,
            password_hash="test_hash",
        )

        session.add(second_user)
        session.commit()
        session.refresh(second_user)

        # ---------------------------------------------------------
        # 9. Verify user isolation.
        # ---------------------------------------------------------

        second_user_connections = get_portal_connections(
            session=session,
            current_user=second_user,
        )

        if second_user_connections:
            raise RuntimeError(
                "Second user can see another user's connections."
            )

        print(
            "User Isolation       : Passed"
        )

        print()
        print(
            "Portal connection API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()