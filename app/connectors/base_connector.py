"""
Base Connector

Defines the interface for all API-based job connectors.
"""

from abc import ABC, abstractmethod

from app.networking.http_client import HttpClient
from app.dto.scraped_job import ScrapedJob


class BaseConnector(ABC):
    """
    Base class for all API connectors.
    """

    def __init__(self) -> None:
        self.http_client = HttpClient()

    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Name of the job source.
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch jobs from the remote API.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Release HTTP resources.
        """
        self.http_client.close()