"""
Test Job Search Service

Integration test for JobSearchService.
"""

# Register all SQLAlchemy models

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

        print("=" * 50)
        print("Job Search Service Test")
        print("=" * 50)

        print()

        active_jobs = service.get_active_jobs()

        print(f"Active Jobs : {len(active_jobs)}")

        print()

        keyword = "Engineer"

        jobs = service.search_jobs(keyword)

        print(f"Search Results for '{keyword}'")
        print("-" * 50)

        if not jobs:
            print("No jobs found.")
        else:
            print(f"Found {len(jobs)} jobs\n")

            for index, job in enumerate(jobs[:10], start=1):
                print(f"{index}. {job.company.name}")
                print(f"   {job.title}")
                print()

            if len(jobs) > 10:
                print(f"... and {len(jobs) - 10} more jobs.")

    finally:
        session.close()


if __name__ == "__main__":
    main()