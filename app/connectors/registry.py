"""
Job Connector Registry

Maps configured scraper names to connector implementations.
"""

from typing import Any

from app.connectors.ashby_connector import AshbyConnector
from app.connectors.base_connector import BaseConnector
from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.lever_connector import LeverConnector
from app.connectors.smartrecruiters_connector import SmartRecruitersConnector


_CONNECTORS: dict[str, type[BaseConnector]] = {
    "greenhouse_scraper": GreenhouseConnector,
    "lever_scraper": LeverConnector,
    "ashby_scraper": AshbyConnector,
    "smartrecruiters_scraper": SmartRecruitersConnector,
}


def get_connector_class(scraper_name: str) -> type[BaseConnector]:
    """
    Resolve a configured scraper name to its connector class.
    """

    try:
        return _CONNECTORS[scraper_name]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported scraper: '{scraper_name}'."
        ) from exc


def create_connector(
    scraper_name: str,
    **kwargs: Any,
) -> BaseConnector:
    """
    Create a connector instance from a configured scraper name.

    Connector-specific constructor arguments are passed explicitly
    through kwargs.
    """

    connector_class = get_connector_class(scraper_name)

    try:
        return connector_class(**kwargs)
    except TypeError as exc:
        raise ValueError(
            f"Invalid configuration for scraper: '{scraper_name}'."
        ) from exc