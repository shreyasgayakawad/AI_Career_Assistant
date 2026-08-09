"""
Credential Service

Provides secure access to encrypted credentials stored on
portal connections.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.portal_connection import PortalConnection
from app.repositories.portal_connection_repository import (
    PortalConnectionRepository,
)
from app.security.credential_encryption import decrypt_credential


class CredentialService:
    """
    Service for retrieving decrypted credentials for
    authenticated external platform connections.
    """

    def __init__(
        self,
        session: Session,
    ):
        self.portal_connection_repository = (
            PortalConnectionRepository(session)
        )

    def get_access_token(
        self,
        user_id: int,
        platform: str,
    ) -> str:
        """
        Retrieve and decrypt an active platform access token.

        Raises ValueError when the connection is missing,
        disabled, inactive, missing credentials, or expired.
        """

        connection = (
            self.portal_connection_repository
            .get_by_user_and_platform(
                user_id=user_id,
                platform=platform,
            )
        )

        if connection is None:
            raise ValueError(
                f"{platform} connection does not exist."
            )

        if not connection.enabled:
            raise ValueError(
                f"{platform} connection is disabled."
            )

        if connection.status != "ACTIVE":
            raise ValueError(
                f"{platform} connection is not active."
            )

        if not connection.credential_reference:
            raise ValueError(
                f"{platform} access credential is not configured."
            )

        if self._is_expired(
            connection,
        ):
            raise ValueError(
                f"{platform} access token has expired."
            )

        try:
            return decrypt_credential(
                connection.credential_reference,
            )
        except ValueError as exc:
            raise ValueError(
                f"{platform} access credential could not be decrypted."
            ) from exc

    @staticmethod
    def _is_expired(
        connection: PortalConnection,
    ) -> bool:
        """
        Determine whether the stored access token has expired.

        Connections without an expiration timestamp are treated
        as non-expiring.
        """

        if connection.token_expires_at is None:
            return False

        expires_at = connection.token_expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc,
            )

        return expires_at <= datetime.now(
            timezone.utc,
        )