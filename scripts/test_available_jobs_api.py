"""
Test Available Jobs API

Integration test for the job listing API.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from app.api.routes.jobs import get_jobs
from app.database.session import SessionLocal
from app.models.application import Application


def main() -> None:
    """
    Test the available jobs API.
    """

    session = SessionLocal()

    try:
        print("=" * 50)
        print("Available Jobs API Test")
        print("=" * 50)

        jobs = get_jobs(
            session=session,
        )

        print()
        print(
            f"Available Job Postings : "
            f"{len(jobs)}"
        )

        for job in jobs[:10]:
            print()
            print(
                f"Posting ID : {job.id}"
            )
            print(
                f"Job ID     : {job.job_id}"
            )
            print(
                f"Title      : {job.title}"
            )
            print(
                f"Company    : {job.company}"
            )
            print(
                f"Location   : {job.location}"
            )
            print(
                f"URL        : {job.posting_url}"
            )

        # Make sure no returned posting has already
        # been applied to.
        for job in jobs:
            application = (
                session.query(Application)
                .filter(
                    Application.job_posting_id == job.id,
                )
                .first()
            )

            if application is not None:
                raise RuntimeError(
                    "An applied job posting was returned "
                    f"by the API: {job.id}"
                )

        print()
        print(
            "Applied Posting Exclusion : Passed"
        )

        # Verify the response contains both identifiers.
        for job in jobs:
            if job.id is None:
                raise RuntimeError(
                    "Posting ID is missing."
                )

            if job.job_id is None:
                raise RuntimeError(
                    "Logical Job ID is missing."
                )

        print(
            "Posting Identity          : Passed"
        )

        print()
        print(
            "Available jobs API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()