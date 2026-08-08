"""
Portal Connection API Test

Tests authenticated portal connection API behavior.
"""

import app.models  # noqa: F401

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.routes.portal_connections import (
    CreatePortalConnectionRequest,
    create_portal_connection,
    get_portal_connections,
)
from app.database.session import SessionLocal
from app.models.portal_connection import PortalConnection
from app.models.user import User
from app.auth.jwt import create_access_token


def main() -> None:
    """
    Test portal connection API behavior.
    """

    session = SessionLocal()

    try:
        user_email = "portal_api_test@example.com"

        # ---------------------------------------------------------
        # Clean up previous test user.
        # ---------------------------------------------------------

        existing_user = (
            session.query(User)
            .filter(User.email == user_email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)
            session.commit()

        # ---------------------------------------------------------
        # Create test user.
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

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
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
        # 2. Retrieve connections.
        # ---------------------------------------------------------

        connections = get_portal_connections(
            session=session,
            current_user=user,
        )

        if len(connections) != 1:
            raise RuntimeError(
                "Expected exactly one portal connection."
            )

        if connections[0].id != create_response.id:
            raise RuntimeError(
                "Retrieved connection ID does not match."
            )

        print(
            "Connection Retrieval : Passed"
        )

        # ---------------------------------------------------------
        # 3. Duplicate connection prevention.
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
        # 4. Create another platform.
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

        print(
            "Multiple Platforms   : Passed"
        )

        # ---------------------------------------------------------
        # 5. Verify user isolation.
        # ---------------------------------------------------------

        second_user = User(
            name="Second Portal API User",
            email="portal_api_second_user@example.com",
            password_hash="test_hash",
        )

        session.add(second_user)
        session.commit()
        session.refresh(second_user)

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