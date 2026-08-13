"""
Test Connector Registry
"""

from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.registry import (
    create_connector,
    get_connector_class,
)


def main() -> None:
    connector_class = get_connector_class(
        "greenhouse_scraper",
    )

    assert connector_class is GreenhouseConnector

    connector = create_connector(
        "greenhouse_scraper",
        company="anthropic",
    )

    assert isinstance(
        connector,
        GreenhouseConnector,
    )

    assert connector.company == "anthropic"

    connector.close()

    try:
        get_connector_class("unknown_scraper")
    except ValueError as exc:
        assert "Unsupported scraper" in str(exc)
    else:
        raise AssertionError(
            "Unknown scraper should raise ValueError."
        )

    try:
        create_connector(
            "greenhouse_scraper",
        )
    except ValueError as exc:
        assert "Invalid configuration" in str(exc)
    else:
        raise AssertionError(
            "Missing connector configuration should raise ValueError."
        )

    print("Connector registry test passed.")


if __name__ == "__main__":
    main()
