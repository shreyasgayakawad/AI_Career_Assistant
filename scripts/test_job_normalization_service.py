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
    # Test 1: Hybrid
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
    # Test 2: Greenhouse On-Site
    # ---------------------------------------------------------------

    onsite_job = ScrapedJob(
        company="Anthropic",
        title="AI Compliance Officer",
        location="Dublin, IE",
        url="https://example.com/onsite",
        work_mode="On-Site",
    )

    normalized_onsite = service.normalize(
        onsite_job,
    )

    assert normalized_onsite.work_mode == "ONSITE"

    # ---------------------------------------------------------------
    # Test 3: Remote
    # ---------------------------------------------------------------

    remote_job = ScrapedJob(
        company="Anthropic",
        title="Software Engineer",
        location="Remote",
        url="https://example.com/remote",
        work_mode="Remote",
    )

    normalized_remote = service.normalize(
        remote_job,
    )

    assert normalized_remote.work_mode == "REMOTE"

    # ---------------------------------------------------------------
    # Test 4: Supported work-mode aliases
    # ---------------------------------------------------------------

    aliases = {
        "REMOTE-FRIENDLY": "REMOTE",
        "REMOTE FRIENDLY": "REMOTE",
        "HYBRID-FRIENDLY": "HYBRID",
        "HYBRID FRIENDLY": "HYBRID",
        "HYBRID (TRAVEL-REQUIRED)": "HYBRID",
        "HYBRID(TRAVEL-REQUIRED)": "HYBRID",
        "ON SITE": "ONSITE",
        "ONSITE": "ONSITE",
        "IN-OFFICE": "ONSITE",
        "IN OFFICE": "ONSITE",
    }

    for raw_value, expected_value in aliases.items():
        normalized = service._normalize_work_mode(
            raw_value,
        )

        assert normalized == expected_value, (
            f"{raw_value!r} should normalize to "
            f"{expected_value!r}, got {normalized!r}"
        )

    # ---------------------------------------------------------------
    # Test 5: Missing work mode
    # ---------------------------------------------------------------

    missing_work_mode = ScrapedJob(
        company="Company",
        title="Title",
        location="Location",
        url="https://example.com/missing",
        work_mode=None,
    )

    normalized_missing = service.normalize(
        missing_work_mode,
    )

    assert normalized_missing.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 6: Blank work mode
    # ---------------------------------------------------------------

    blank_work_mode = ScrapedJob(
        company="Company",
        title="Title",
        location="Location",
        url="https://example.com/blank",
        work_mode="   ",
    )

    normalized_blank = service.normalize(
        blank_work_mode,
    )

    assert normalized_blank.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 7: Invalid work mode
    # ---------------------------------------------------------------

    invalid_work_mode = ScrapedJob(
        company="Company",
        title="Title",
        location="Location",
        url="https://example.com/invalid",
        work_mode="Something Else",
    )

    normalized_invalid = service.normalize(
        invalid_work_mode,
    )

    assert normalized_invalid.work_mode == "UNKNOWN"

    # ---------------------------------------------------------------
    # Test 8: Optional fields
    # ---------------------------------------------------------------

    empty_fields = ScrapedJob(
        company="Company",
        title="Title",
        location="Location",
        url="https://example.com",
        work_mode="HYBRID",
        description="   ",
        external_job_id="   ",
        salary="   ",
    )

    normalized_empty = service.normalize(
        empty_fields,
    )

    assert normalized_empty.description is None
    assert normalized_empty.external_job_id is None
    assert normalized_empty.salary is None
    assert normalized_empty.work_mode == "HYBRID"

    print(
        "Job normalization service test passed."
    )


if __name__ == "__main__":
    main()