"""
Test Job Discovery Service

Integration test for JobDiscoveryService.
"""

# Register all SQLAlchemy models

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.services.job_discovery_service import JobDiscoveryService


def main() -> None:
    """
    Test Greenhouse job discovery and import.
    """

    session = SessionLocal()

    try:
        service = JobDiscoveryService(session)

        imported, skipped = service.discover(
            scraper_name="greenhouse_scraper",
            source_name="Greenhouse",
            connector_kwargs={
                "company": "anthropic",
            },
        )

        print("=" * 50)
        print("Job Discovery Service Test")
        print("=" * 50)
        print(f"Imported : {imported}")
        print(f"Skipped  : {skipped}")

    finally:
        session.close()


if __name__ == "__main__":
    main()