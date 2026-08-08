"""
LinkedIn Portal

Provides the LinkedIn implementation of the BasePortal interface.
"""

from app.config.settings import LINKEDIN_ENABLED
from app.connectors.base_portal import BasePortal


class LinkedInPortal(BasePortal):
    """
    Portal adapter for LinkedIn.
    """

    @property
    def platform_name(self) -> str:
        """
        Return the platform name.
        """
        return "LinkedIn"

    def connect(self) -> bool:
        """
        Establish a LinkedIn connection.

        Actual authentication will be implemented later.
        """

        if not LINKEDIN_ENABLED:
            raise RuntimeError(
                "LinkedIn integration is disabled."
            )

        raise NotImplementedError(
            "LinkedIn authentication is not implemented yet."
        )

    def disconnect(self) -> None:
        """
        Disconnect from LinkedIn.

        Session management will be implemented later.
        """

        if not LINKEDIN_ENABLED:
            raise RuntimeError(
                "LinkedIn integration is disabled."
            )

        raise NotImplementedError(
            "LinkedIn disconnection is not implemented yet."
        )