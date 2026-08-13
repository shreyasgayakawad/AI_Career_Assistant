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

    job = ScrapedJob(
        company="  Anthropic  ",
        title="  Software Engineer  ",
        location="  Remote  ",
        url="  https://example.com/job  ",
        description="  Test description  ",
        external_job_id="  12345  ",
        salary="  $150,000  ",
    )

    normalized = service.normalize(job)

    assert normalized.company == "Anthropic"
    assert normalized.title == "Software Engineer"
    assert normalized.location == "Remote"
    assert normalized.url == "https://example.com/job"
    assert normalized.description == "Test description"
    assert normalized.external_job_id == "12345"
    assert normalized.salary == "$150,000"

    empty_fields = ScrapedJob(
        company="Company",
        title="Title",
        location="Location",
        url="https://example.com",
        description="   ",
        external_job_id="   ",
        salary="   ",
    )

    normalized_empty = service.normalize(empty_fields)

    assert normalized_empty.description is None
    assert normalized_empty.external_job_id is None
    assert normalized_empty.salary is None

    print("Job normalization service test passed.")


if __name__ == "__main__":
    main()