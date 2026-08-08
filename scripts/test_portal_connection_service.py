"""
Portal Connection Service Test

Tests business logic for user portal connections.
"""

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.user import User
from app.services.portal_connection_service import (
    PortalConnectionService,
)


def main() -> None:
    """
    Test PortalConnectionService behavior.
    """

    session = SessionLocal()

    try:
        user_email = "portal_service_test@example.com"

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
            name="Portal Service Test User",
            email=user_email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        service = PortalConnectionService(
            session,
        )

        # ---------------------------------------------------------
        # Create LinkedIn connection.
        # ---------------------------------------------------------

        connection = service.create_connection(
            user_id=user.id,
            platform="LinkedIn",
            login_email=user.email,
        )

        print()
        print("# Portal Connection Service Test")
        print()
        print(
            f"Created Connection ID : {connection.id}"
        )
        print(
            f"Platform              : {connection.platform}"
        )
        print(
            f"Login Email           : {connection.login_email}"
        )

        if connection.user_id != user.id:
            raise RuntimeError(
                "Connection user ID does not match."
            )

        if connection.platform != "LinkedIn":
            raise RuntimeError(
                "Connection platform does not match."
            )

        if connection.enabled is not True:
            raise RuntimeError(
                "New connection should be enabled."
            )

        if connection.status != "ACTIVE":
            raise RuntimeError(
                "New connection should be ACTIVE."
            )

        print()
        print("Connection Creation : Passed")

        # ---------------------------------------------------------
        # Retrieve connection.
        # ---------------------------------------------------------

        found_connection = service.get_connection(
            user_id=user.id,
            platform="LinkedIn",
        )

        if found_connection is None:
            raise RuntimeError(
                "Created connection was not found."
            )

        if found_connection.id != connection.id:
            raise RuntimeError(
                "Retrieved connection ID does not match."
            )

        print(
            "Connection Retrieval : Passed"
        )

        # ---------------------------------------------------------
        # Duplicate connection prevention.
        # ---------------------------------------------------------

        try:
            service.create_connection(
                user_id=user.id,
                platform="LinkedIn",
                login_email=user.email,
            )

            raise RuntimeError(
                "Duplicate portal connection was created."
            )

        except ValueError as exc:
            if str(exc) != (
                "LinkedIn connection already exists."
            ):
                raise RuntimeError(
                    "Unexpected duplicate connection error."
                )

        print(
            "Duplicate Prevention : Passed"
        )

        # ---------------------------------------------------------
        # Different supported platforms are allowed.
        # ---------------------------------------------------------

        naukri_connection = service.create_connection(
            user_id=user.id,
            platform="Naukri",
            login_email=user.email,
        )

        surelyremote_connection = (
            service.create_connection(
                user_id=user.id,
                platform="SurelyRemote",
                login_email=user.email,
            )
        )

        if naukri_connection.platform != "Naukri":
            raise RuntimeError(
                "Naukri connection was not created correctly."
            )

        if surelyremote_connection.platform != "SurelyRemote":
            raise RuntimeError(
                "SurelyRemote connection was not created correctly."
            )

        print(
            "Multiple Platforms   : Passed"
        )

        # ---------------------------------------------------------
        # Unsupported platform rejection.
        # ---------------------------------------------------------

        try:
            service.create_connection(
                user_id=user.id,
                platform="Remotely",
                login_email=user.email,
            )

            raise RuntimeError(
                "Unsupported platform was accepted."
            )

        except ValueError as exc:
            if str(exc) != (
                "Unsupported job platform: Remotely."
            ):
                raise RuntimeError(
                    "Unexpected unsupported-platform error."
                )

        print(
            "Unsupported Platform  : Passed"
        )

        # ---------------------------------------------------------
        # Retrieve all connections.
        # ---------------------------------------------------------

        connections = service.get_all_connections(
            user_id=user.id,
        )

        if len(connections) != 3:
            raise RuntimeError(
                "Expected exactly three portal connections."
            )

        platforms = {
            connection.platform
            for connection in connections
        }

        expected_platforms = {
            "LinkedIn",
            "Naukri",
            "SurelyRemote",
        }

        if platforms != expected_platforms:
            raise RuntimeError(
                "Unexpected platforms returned."
            )

        print(
            "All User Connections  : Passed"
        )

        print()
        print(
            "Portal connection service test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()