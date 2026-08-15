"""
Test Job Search Service

Integration test for JobSearchService.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.services.job_search_service import JobSearchService


def main() -> None:
    """
    Test JobSearchService.
    """

    session = SessionLocal()

    try:
        service = JobSearchService(session)

        print("=" * 60)
        print("Job Search Service Test")
        print("=" * 60)

        # -----------------------------------------------------------
        # Test 1: Active logical jobs.
        # -----------------------------------------------------------

        active_jobs = service.get_active_jobs()

        print()
        print(
            f"Active Jobs : {len(active_jobs)}"
        )

        # -----------------------------------------------------------
        # Test 2: Keyword search.
        # -----------------------------------------------------------

        keyword = "Engineer"

        jobs = service.search_jobs(
            keyword=keyword,
        )

        print()
        print(
            f"Search Results for '{keyword}'"
        )
        print("-" * 60)

        if not jobs:
            print("No jobs found.")
        else:
            print(
                f"Found {len(jobs)} jobs"
            )

            for index, job in enumerate(
                jobs[:10],
                start=1,
            ):
                print(
                    f"{index}. "
                    f"{job.company.name}"
                )
                print(
                    f"   {job.title}"
                )

            if len(jobs) > 10:
                print(
                    f"... and "
                    f"{len(jobs) - 10} more jobs."
                )

        # -----------------------------------------------------------
        # Test 3: Work mode filtering.
        # -----------------------------------------------------------

        for work_mode in (
            "REMOTE",
            "HYBRID",
            "ONSITE",
            "UNKNOWN",
        ):
            postings = (
                service.search_available_postings(
                    work_mode=work_mode,
                )
            )

            for posting in postings:
                if posting.work_mode != work_mode:
                    raise RuntimeError(
                        "Work mode filter returned "
                        f"'{posting.work_mode}' for "
                        f"requested '{work_mode}'."
                    )

            print()
            print(
                f"{work_mode} postings : "
                f"{len(postings)}"
            )

        # -----------------------------------------------------------
        # Test 4: Invalid work mode.
        # -----------------------------------------------------------

        try:
            service.search_available_postings(
                work_mode="INVALID",
            )

            raise RuntimeError(
                "Expected ValueError for "
                "unsupported work mode."
            )

        except ValueError:
            print(
                "Invalid work mode rejection : Passed"
            )

        # -----------------------------------------------------------
        # Test 5: No work mode filter.
        # -----------------------------------------------------------

        all_postings = (
            service.search_available_postings()
        )

        print()
        print(
            f"Available Postings : "
            f"{len(all_postings)}"
        )

        print()
        print(
            "Job search service test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()