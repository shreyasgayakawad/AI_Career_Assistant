"""
Test Job Search

Integration test for JobRepository search methods.
"""

# Register all SQLAlchemy models

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.repositories.job_repository import JobRepository


def main() -> None:
    """
    Test JobRepository search methods.
    """

    session = SessionLocal()

    try:
        repository = JobRepository(session)

        print("=" * 50)
        print("Job Search Test")
        print("=" * 50)

        print()

        active_jobs = repository.get_active_jobs()

        print(f"Active Jobs : {len(active_jobs)}")

        print()

        keyword = "Engineer"

        jobs = repository.search(keyword=keyword)

        print(f"Search Results for '{keyword}'")
        print("-" * 50)

        if not jobs:
            print("No jobs found.")
        else:
            for index, job in enumerate(jobs, start=1):
                print(f"{index}. {job.company.name}")
                print(f"   {job.title}")
                print()

        print("Job search test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()