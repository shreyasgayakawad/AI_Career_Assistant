"""
Job Discovery Service

Coordinates job discovery connectors and job importing.
"""

from sqlalchemy.orm import Session

from app.connectors.registry import create_connector
from app.services.job_import_service import JobImportService


class JobDiscoveryService:
    """
    Coordinates external job discovery and database import.
    """

    def __init__(self, session: Session):
        self.job_import_service = JobImportService(session)

    def discover(
        self,
        *,
        scraper_name: str,
        source_name: str,
        connector_kwargs: dict[str, object] | None = None,
    ) -> tuple[int, int]:
        """
        Fetch jobs from a connector and import them.

        Returns:
            (imported_count, skipped_count)
        """

        connector_kwargs = connector_kwargs or {}

        connector = create_connector(
            scraper_name,
            **connector_kwargs,
        )

        try:
            scraped_jobs = connector.fetch_jobs()

            return self.job_import_service.import_jobs(
                scraped_jobs=scraped_jobs,
                source_name=source_name,
            )
        finally:
            connector.close()