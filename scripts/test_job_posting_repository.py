"""
Test Job Posting Repository

Integration test for application-aware job posting search.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.job_posting import JobPosting
from app.repositories.job_posting_repository import JobPostingRepository


def main() -> None:
    """
    Test JobPostingRepository search behavior.
    """

    session = SessionLocal()

    try:
        repository = JobPostingRepository(session)

        applied_posting = session.query(JobPosting).first()

        if applied_posting is None:
            raise RuntimeError(
                "No job posting exists. "
                "Run the Greenhouse import first."
            )

        print("=" * 50)
        print("Job Posting Repository Test")
        print("=" * 50)

        print(
            f"Applied Posting ID : "
            f"{applied_posting.id}"
        )
        print(
            f"Job Title          : "
            f"{applied_posting.title}"
        )

        # Create a temporary second posting for the same logical job.
        # It is flushed but never committed, so the test does not
        # permanently modify the database.
        temporary_posting = JobPosting(
            job_id=applied_posting.job_id,
            source_id=applied_posting.source_id,
            external_job_id=(
                f"test-{applied_posting.id}-unapplied"
            ),
            posting_url=(
                f"https://test.local/"
                f"job/{applied_posting.id}-unapplied"
            ),
            title=applied_posting.title,
            location=applied_posting.location,
            salary=applied_posting.salary,
            description=applied_posting.description,
            posted_date=applied_posting.posted_date,
            status="ACTIVE",
        )

        session.add(temporary_posting)
        session.flush()

        # 1. Applied posting should be excluded.
        results = repository.search()

        result_ids = {
            posting.id
            for posting in results
        }

        if applied_posting.id in result_ids:
            raise RuntimeError(
                "Applied posting was returned by search."
            )

        print()
        print(
            "Applied Posting Excluded : Passed"
        )

        # 2. Unapplied posting should be returned.
        if temporary_posting.id not in result_ids:
            raise RuntimeError(
                "Unapplied posting was not returned."
            )

        print(
            "Unapplied Posting Included: Passed"
        )

        # 3. Keyword filtering should work.
        keyword_results = repository.search(
            keyword=temporary_posting.title,
        )

        keyword_ids = {
            posting.id
            for posting in keyword_results
        }

        if temporary_posting.id not in keyword_ids:
            raise RuntimeError(
                "Keyword filtering failed."
            )

        print(
            "Keyword Filtering         : Passed"
        )

        # 4. Company filtering should work.
        company = applied_posting.job.company

        company_results = repository.search(
            company=company,
        )

        company_ids = {
            posting.id
            for posting in company_results
        }

        if temporary_posting.id not in company_ids:
            raise RuntimeError(
                "Company filtering failed."
            )

        print(
            "Company Filtering         : Passed"
        )

        print()
        print("Job posting repository test passed.")

        # Roll back the temporary posting.
        session.rollback()

    finally:
        session.close()


if __name__ == "__main__":
    main()