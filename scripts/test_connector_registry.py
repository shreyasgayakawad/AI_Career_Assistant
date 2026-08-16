"""
Test Connector Registry
"""

from app.connectors.ashby_connector import AshbyConnector
from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.lever_connector import LeverConnector
from app.connectors.registry import (
    create_connector,
    get_connector_class,
)


def main() -> None:
    # ---------------------------------------------------------
    # Greenhouse Scraper
    # ---------------------------------------------------------
    connector_class = get_connector_class("greenhouse_scraper")
    assert connector_class is GreenhouseConnector

    connector = create_connector("greenhouse_scraper", company="anthropic")
    assert isinstance(connector, GreenhouseConnector)
    assert connector.company == "anthropic"
    connector.close()

    # ---------------------------------------------------------
    # Lever Scraper
    # ---------------------------------------------------------
    lever_class = get_connector_class("lever_scraper")
    assert lever_class is LeverConnector

    lever_connector = create_connector("lever_scraper", company="palantir")
    assert isinstance(lever_connector, LeverConnector)
    assert lever_connector.company == "palantir"
    lever_connector.close()

    # ---------------------------------------------------------
    # Ashby Scraper
    # ---------------------------------------------------------
    ashby_class = get_connector_class("ashby_scraper")
    assert ashby_class is AshbyConnector

    ashby_connector = create_connector("ashby_scraper", company="linear")
    assert isinstance(ashby_connector, AshbyConnector)
    assert ashby_connector.company == "linear"
    ashby_connector.close()

    # ---------------------------------------------------------
    # Error Handling
    # ---------------------------------------------------------
    try:
        get_connector_class("unknown_scraper")
    except ValueError as exc:
        assert "Unsupported scraper" in str(exc)
    else:
        raise AssertionError("Unknown scraper should raise ValueError.")

    try:
        create_connector("greenhouse_scraper")
    except ValueError as exc:
        assert "Invalid configuration" in str(exc)
    else:
        raise AssertionError(
            "Missing connector configuration should raise ValueError."
        )

    print("Connector registry test passed.")


if __name__ == "__main__":
    main()