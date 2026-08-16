"""
Test Job Search Posting Service

Integration test for searching available job postings.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.services.job_search_service import JobSearchService


def main() -> None:
    """
    Test available job posting search.
    """

    session = SessionLocal()

    try:
        service = JobSearchService(session)

        print("=" * 50)
        print("Job Search Posting Service Test")
        print("=" * 50)

        # ---------------------------------------------------------
        # 1. Search all available postings
        # ---------------------------------------------------------

        postings = service.search_available_postings()

        print()
        print(
            f"Available Postings : "
            f"{len(postings)}"
        )

        for posting in postings[:10]:
            print(
                f"{posting.id} | "
                f"{posting.title} | "
                f"{posting.job.company.name}"
            )

        # Make sure no applied posting is returned.
        for posting in postings:
            if len(posting.applications) > 0:
                raise RuntimeError(
                    "An applied posting was returned."
                )

        print()
        print(
            "Applied Posting Exclusion : Passed"
        )

        # ---------------------------------------------------------
        # 2. Keyword filtering
        # ---------------------------------------------------------

        keyword_postings = (
            service.search_available_postings(
                keyword="Engineer",
            )
        )

        print(
            f"Engineer Results          : "
            f"{len(keyword_postings)}"
        )

        # ---------------------------------------------------------
        # 3. Non-matching keyword should return zero results
        # ---------------------------------------------------------

        missing_keyword_postings = (
            service.search_available_postings(
                keyword="THIS_KEYWORD_SHOULD_NOT_EXIST_12345",
            )
        )

        if missing_keyword_postings:
            raise RuntimeError(
                "Keyword filtering is not working. "
                f"Found {len(missing_keyword_postings)} results."
            )

        print(
            "Non-Matching Keyword Filtering : Passed"
        )

        # ---------------------------------------------------------
        # 4. Company filtering
        # ---------------------------------------------------------

        company_postings = (
            service.search_available_postings(
                company_name="Anthropic",
            )
        )

        print(
            f"Anthropic Results         : "
            f"{len(company_postings)}"
        )

        for posting in company_postings:
            if posting.job.company.name.lower() != "anthropic":
                raise RuntimeError(
                    "Company filtering returned "
                    "a posting from another company."
                )

        print(
            "Company Filtering         : Passed"
        )

        print()
        print(
            "Job search posting service "
            "test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()