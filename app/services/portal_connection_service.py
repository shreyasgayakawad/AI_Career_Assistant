"""
Portal Connection Service

Provides business logic for managing user portal connections.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.config.platforms import JobPlatform
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

        self._validate_platform(platform)

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
        external_user_id: str | None = None,
        oauth_scopes: str | None = None,
        token_expires_at: datetime | None = None,
    ) -> PortalConnection:
        """
        Create a portal connection for a user.

        Raises ValueError if the platform is unsupported
        or the user already has a connection for it.
        """

        self._validate_platform(platform)

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
            external_user_id=external_user_id,
            credential_reference=credential_reference,
            oauth_scopes=oauth_scopes,
            token_expires_at=token_expires_at,
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

    @staticmethod
    def _validate_platform(platform: str) -> None:
        """
        Validate that the requested platform is supported.
        """

        supported_platforms = {
            supported_platform.value
            for supported_platform in JobPlatform
        }

        if platform not in supported_platforms:
            raise ValueError(
                f"Unsupported job platform: {platform}."
            )