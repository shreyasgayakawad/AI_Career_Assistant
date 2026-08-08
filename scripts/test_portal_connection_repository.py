"""
Portal Connection Repository Test

Tests database operations for portal connections.
"""

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.portal_connection import PortalConnection
from app.models.user import User
from app.repositories.portal_connection_repository import (
    PortalConnectionRepository,
)


def main() -> None:
    """
    Test PortalConnectionRepository behavior.
    """

    session = SessionLocal()

    try:
        user_email = "portal_repository_test@example.com"

        # ---------------------------------------------------------
        # Clean up previous test data.
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
            name="Portal Repository Test User",
            email=user_email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        repository = PortalConnectionRepository(
            session,
        )

        # ---------------------------------------------------------
        # Create portal connection.
        # ---------------------------------------------------------

        connection = PortalConnection(
            user_id=user.id,
            platform="LinkedIn",
            login_email=user.email,
            credential_reference=None,
            enabled=True,
            status="ACTIVE",
        )

        created_connection = repository.create(
            connection,
        )

        print()
        print("# Portal Connection Repository Test")
        print()
        print(
            f"Created Connection ID : "
            f"{created_connection.id}"
        )
        print(
            f"User ID               : "
            f"{created_connection.user_id}"
        )
        print(
            f"Platform              : "
            f"{created_connection.platform}"
        )

        print()
        print("Connection Creation : Passed")

        # ---------------------------------------------------------
        # Find by user and platform.
        # ---------------------------------------------------------

        found_connection = (
            repository.get_by_user_and_platform(
                user_id=user.id,
                platform="LinkedIn",
            )
        )

        if found_connection is None:
            raise RuntimeError(
                "Portal connection was not found."
            )

        if found_connection.id != created_connection.id:
            raise RuntimeError(
                "Retrieved connection ID does not match."
            )

        print(
            "User + Platform Lookup : Passed"
        )

        # ---------------------------------------------------------
        # Missing platform.
        # ---------------------------------------------------------

        missing_connection = (
            repository.get_by_user_and_platform(
                user_id=user.id,
                platform="Naukri",
            )
        )

        if missing_connection is not None:
            raise RuntimeError(
                "Unexpected connection returned for Naukri."
            )

        print(
            "Missing Platform Lookup : Passed"
        )

        # ---------------------------------------------------------
        # Get all connections for user.
        # ---------------------------------------------------------

        connections = (
            repository.get_all_for_user(
                user_id=user.id,
            )
        )

        if len(connections) != 1:
            raise RuntimeError(
                "Expected exactly one portal connection."
            )

        if connections[0].platform != "LinkedIn":
            raise RuntimeError(
                "Unexpected platform returned."
            )

        print(
            "User Connections Lookup : Passed"
        )

        print()
        print(
            "Portal connection repository test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()