"""
Job Discovery Service

Coordinates job discovery connectors, normalization,
and job importing.
"""

from sqlalchemy.orm import Session

from app.connectors.registry import create_connector
from app.services.job_import_service import JobImportService
from app.services.job_normalization_service import (
    JobNormalizationService,
)


class JobDiscoveryService:
    """
    Coordinates external job discovery and database import.
    """

    def __init__(self, session: Session):
        self.job_import_service = JobImportService(
            session,
        )
        self.job_normalization_service = (
            JobNormalizationService()
        )

    def discover(
        self,
        *,
        scraper_name: str,
        source_name: str,
        connector_kwargs: dict[str, object] | None = None,
    ) -> tuple[int, int]:
        """
        Fetch, normalize, and import jobs from a connector.

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

            normalized_jobs = [
                self.job_normalization_service.normalize(
                    scraped_job,
                )
                for scraped_job in scraped_jobs
            ]

            return self.job_import_service.import_jobs(
                scraped_jobs=normalized_jobs,
                source_name=source_name,
            )
        finally:
            connector.close()