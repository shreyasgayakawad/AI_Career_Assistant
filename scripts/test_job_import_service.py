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
    Test importing a single scraped job.
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

        posting = service.import_job(
            scraped_job=scraped_job,
            source_name="Greenhouse",
        )

        print("=" * 50)
        print("Job Import Service Test")
        print("=" * 50)

        if posting is None:
            print("Job posting already exists.")
        else:
            print(f"Posting ID      : {posting.id}")
            print(f"Company         : {posting.job.company.name}")
            print(f"Job             : {posting.job.title}")
            print(f"Source          : {posting.source.name}")
            print(f"Posting URL     : {posting.posting_url}")

    finally:
        session.close()


if __name__ == "__main__":
    main()