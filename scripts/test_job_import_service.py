"""
Test Job Import Service

Integration test for JobImportService.
"""

# Register all SQLAlchemy models
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.dto.scraped_job import ScrapedJob
from app.services.job_import_service import JobImportService


def main() -> None:
    """
    Test JobImportService business methods.
    """

    session = SessionLocal()

    try:
        service = JobImportService(session)

        scraped_job = ScrapedJob(
            company="Anthropic",
            title="Software Engineer",
            location="Remote",
            url="https://example.com/job",
            description="Test Job",
        )

        company = service.get_or_create_company(scraped_job.company)
        source = service.get_source("Greenhouse")

        print("=" * 50)
        print("Job Import Service Test")
        print("=" * 50)

        print(f"Company ID   : {company.id}")
        print(f"Company Name : {company.name}")

        print()

        print(f"Source ID    : {source.id}")
        print(f"Source Name  : {source.name}")

    finally:
        session.close()


if __name__ == "__main__":
    main()