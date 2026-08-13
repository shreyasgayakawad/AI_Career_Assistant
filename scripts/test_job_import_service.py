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
    Test job import and duplicate detection.
    """

    session = SessionLocal()

    try:
        service = JobImportService(session)

        print("=" * 60)
        print("Job Import Service Test")
        print("=" * 60)

        # ---------------------------------------------------------------
        # Test 1: Import a job with a unique URL.
        # ---------------------------------------------------------------

        url_test_job = ScrapedJob(
            company="Anthropic",
            title="Test URL Duplicate Detection",
            location="Remote",
            url="https://example.com/job-url-duplicate-test",
            description="URL duplicate detection test.",
            external_job_id=None,
        )

        first_url_import = service.import_job(
            scraped_job=url_test_job,
            source_name="Greenhouse",
        )

        # The first import may already exist if this test has been run
        # previously. That is acceptable.
        if first_url_import is not None:
            print("URL test seed       : imported")
        else:
            print("URL test seed       : already exists")

        # ---------------------------------------------------------------
        # Test 1b: Same URL must be skipped.
        # ---------------------------------------------------------------

        duplicate_url_job = ScrapedJob(
            company="Anthropic",
            title="Different Title",
            location="Different Location",
            url="https://example.com/job-url-duplicate-test",
            description="This must not create another posting.",
            external_job_id="different-external-id",
        )

        duplicate_url_result = service.import_job(
            scraped_job=duplicate_url_job,
            source_name="Greenhouse",
        )

        assert duplicate_url_result is None, (
            "Duplicate posting URL should be skipped."
        )

        print("URL duplicate      : skipped")

        # ---------------------------------------------------------------
        # Test 2: Import a job with a unique external job ID.
        # ---------------------------------------------------------------

        external_id_test_job = ScrapedJob(
            company="Anthropic",
            title="Test External ID Duplicate Detection",
            location="Remote",
            url="https://example.com/job-external-id-test",
            description="External ID duplicate detection test.",
            external_job_id="greenhouse-test-external-id-001",
        )

        first_external_id_import = service.import_job(
            scraped_job=external_id_test_job,
            source_name="Greenhouse",
        )

        # The first import may already exist if this test has been run
        # previously. That is acceptable.
        if first_external_id_import is not None:
            print("External ID seed    : imported")
        else:
            print("External ID seed    : already exists")

        # ---------------------------------------------------------------
        # Test 2b: Same source + external_job_id must be skipped,
        # even when the posting URL is different.
        # ---------------------------------------------------------------

        duplicate_external_id_job = ScrapedJob(
            company="Anthropic",
            title="Another Title",
            location="Another Location",
            url="https://example.com/job-external-id-different-url",
            description="This must not create another posting.",
            external_job_id="greenhouse-test-external-id-001",
        )

        duplicate_external_id_result = service.import_job(
            scraped_job=duplicate_external_id_job,
            source_name="Greenhouse",
        )

        assert duplicate_external_id_result is None, (
            "Duplicate source + external_job_id should be skipped."
        )

        print("External ID duplicate: skipped")

        print()
        print("All job import tests passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()