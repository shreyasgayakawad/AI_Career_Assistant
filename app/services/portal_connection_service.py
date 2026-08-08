"""
Portal Connection Service

Provides business logic for managing user portal connections.
"""

from sqlalchemy.orm import Session

from app.models.portal_connection import PortalConnection
from app.repositories.portal_connection_repository import (
    PortalConnectionRepository,
)


class PortalConnectionService:
    """
    Business service for portal connections.
    """

    def __init__(self, session: Session):
        self.portal_connection_repository = (
            PortalConnectionRepository(session)
        )

    def get_connection(
        self,
        user_id: int,
        platform: str,
    ) -> PortalConnection | None:
        """
        Retrieve a user's connection for a platform.
        """

        return (
            self.portal_connection_repository
            .get_by_user_and_platform(
                user_id=user_id,
                platform=platform,
            )
        )

    def create_connection(
        self,
        user_id: int,
        platform: str,
        login_email: str,
        credential_reference: str | None = None,
    ) -> PortalConnection:
        """
        Create a portal connection for a user.

        Raises ValueError if the user already has
        a connection for the platform.
        """

        existing_connection = (
            self.portal_connection_repository
            .get_by_user_and_platform(
                user_id=user_id,
                platform=platform,
            )
        )

        if existing_connection is not None:
            raise ValueError(
                f"{platform} connection already exists."
            )

        connection = PortalConnection(
            user_id=user_id,
            platform=platform,
            login_email=login_email,
            credential_reference=credential_reference,
            enabled=True,
            status="ACTIVE",
        )

        return self.portal_connection_repository.create(
            connection,
        )

    def get_all_connections(
        self,
        user_id: int,
    ) -> list[PortalConnection]:
        """
        Retrieve all portal connections belonging to a user.
        """

        return (
            self.portal_connection_repository
            .get_all_for_user(
                user_id=user_id,
            )
        )