"""
Import Greenhouse Jobs

Imports all jobs from a Greenhouse board into the database.
"""

# Register all SQLAlchemy models
import app.models  # noqa: F401

from app.connectors.greenhouse_connector import GreenhouseConnector
from app.database.session import SessionLocal
from app.services.job_import_service import JobImportService


def main() -> None:
    """
    Import all Greenhouse jobs.
    """

    connector = GreenhouseConnector("anthropic")
    session = SessionLocal()

    try:
        service = JobImportService(session)

        jobs = connector.fetch_jobs()

        imported, skipped = service.import_jobs(
            scraped_jobs=jobs,
            source_name=connector.source_name,
        )

        print("=" * 50)
        print("Greenhouse Import")
        print("=" * 50)
        print(f"Source        : {connector.source_name}")
        print(f"Company Board : anthropic")
        print(f"Jobs Fetched  : {len(jobs)}")
        print()
        print(f"Imported      : {imported}")
        print(f"Skipped       : {skipped}")

    finally:
        connector.close()
        session.close()


if __name__ == "__main__":
    main()