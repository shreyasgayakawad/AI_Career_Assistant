"""
Job Connector Registry

Maps configured scraper names to connector implementations.
"""

from app.connectors.base_connector import BaseConnector
from app.connectors.greenhouse_connector import GreenhouseConnector


_CONNECTORS: dict[str, type[BaseConnector]] = {
    "greenhouse_scraper": GreenhouseConnector,
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
