"""
Test Job Normalization Service
"""

from app.dto.scraped_job import ScrapedJob
from app.services.job_normalization_service import (
    JobNormalizationService,
)


def main() -> None:
    """
    Test normalization of scraped job data.
    """

    service = JobNormalizationService()

    # ---------------------------------------------------------------
    # Test 1: Hybrid work mode.
    # ---------------------------------------------------------------

    hybrid_job = ScrapedJob(
        company="  Anthropic  ",
        title="  Software Engineer  ",
        location="  San Francisco, CA  ",
        url="  https://example.com/hybrid  ",
        work_mode="  hybrid  ",
        description="  Test description  ",
        external_job_id="  12345  ",
        salary="  $150,000  ",
    )

    normalized_hybrid = service.normalize(
        hybrid_job,
    )

    assert normalized_hybrid.company == "Anthropic"
    assert normalized_hybrid.title == "Software Engineer"
    assert normalized_hybrid.location == "San Francisco, CA"
    assert normalized_hybrid.url == (
        "https://example.com/hybrid"
    )
    assert normalized_hybrid.work_mode == "HYBRID"
    assert normalized_hybrid.description == (
        "Test description"
    )
    assert normalized_hybrid.external_job_id == "12345"
    assert normalized_hybrid.salary == "$150,000"

    # ---------------------------------------------------------------
    # Test 2: Remote work mode with no location.
    # ---------------------------------------------------------------

    remote_job = ScrapedJob(
        company="Company",
        title="Remote Engineer",
        location=None,
        url="https://example.com/remote",
        work_mode="remote",
    )

    normalized_remote = service.normalize(
        remote_job,
    )

    assert normalized_remote.location is None
    assert normalized_remote.work_mode == "REMOTE"

    # ---------------------------------------------------------------
    # Test 3: On-site work mode.
    # ---------------------------------------------------------------

    onsite_job = ScrapedJob(
        company="Company",
        title="Onsite Engineer",
        location="New York, NY",
        url="https://example.com/onsite",
        work_mode="onsite",
    )

    normalized_onsite = service.normalize(
        onsite_job,
    )

    assert normalized_onsite.work_mode == "ONSITE"

    # ---------------------------------------------------------------
    # Test 4: Missing work mode becomes UNKNOWN.
    # ---------------------------------------------------------------

    missing_mode_job = ScrapedJob(
        company="Company",
        title="Unknown Mode Engineer",
        location=None,
        url="https://example.com/missing",
        work_mode=None,
    )

    normalized_missing = service.normalize(
        missing_mode_job,
    )

    assert normalized_missing.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 5: Blank work mode becomes UNKNOWN.
    # ---------------------------------------------------------------

    blank_mode_job = ScrapedJob(
        company="Company",
        title="Blank Mode Engineer",
        location="Remote",
        url="https://example.com/blank",
        work_mode="   ",
    )

    normalized_blank = service.normalize(
        blank_mode_job,
    )

    assert normalized_blank.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 6: Unsupported work mode becomes UNKNOWN.
    # ---------------------------------------------------------------

    unsupported_mode_job = ScrapedJob(
        company="Company",
        title="Unsupported Mode Engineer",
        location="Somewhere",
        url="https://example.com/unsupported",
        work_mode="flexible",
    )

    normalized_unsupported = service.normalize(
        unsupported_mode_job,
    )

    assert normalized_unsupported.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 7: Optional text fields become None when blank.
    # ---------------------------------------------------------------

    empty_fields = ScrapedJob(
        company="Company",
        title="Title",
        location="   ",
        url="https://example.com/empty",
        work_mode="REMOTE",
        description="   ",
        external_job_id="   ",
        salary="   ",
    )

    normalized_empty = service.normalize(
        empty_fields,
    )

    assert normalized_empty.location is None
    assert normalized_empty.description is None
    assert normalized_empty.external_job_id is None
    assert normalized_empty.salary is None
    assert normalized_empty.work_mode == "REMOTE"

    print("Job normalization service test passed.")


if __name__ == "__main__":
    main()