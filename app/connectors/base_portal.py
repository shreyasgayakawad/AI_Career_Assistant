"""
Base Portal

Defines the interface for user-connected job portals.

This is separate from BaseConnector, which is used for
job-listing discovery through public or API-based sources.
"""

from abc import ABC, abstractmethod


class BasePortal(ABC):
    """
    Base class for authenticated job portal integrations.
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        Return the name of the supported job platform.
        """
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the job portal.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the portal connection.
        """
        raise NotImplementedError