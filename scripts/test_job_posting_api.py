"""
Test Job Posting API

Integration test for retrieving an individual job posting.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.job_postings import get_job_posting
from app.database.session import SessionLocal


def main() -> None:
    """
    Test the job posting API.
    """

    session = SessionLocal()

    try:
        print("=" * 50)
        print("Job Posting API Test")
        print("=" * 50)

        posting_id = 179

        posting = get_job_posting(
            posting_id=posting_id,
            session=session,
        )

        print()
        print(
            f"Posting ID : {posting.id}"
        )
        print(
            f"Job ID     : {posting.job_id}"
        )
        print(
            f"Title      : {posting.title}"
        )
        print(
            f"Company    : {posting.company}"
        )
        print(
            f"Location   : {posting.location}"
        )
        print(
            f"URL        : {posting.posting_url}"
        )

        if posting.id != posting_id:
            raise RuntimeError(
                "Returned posting ID does not match "
                "requested posting ID."
            )

        print()
        print(
            "Posting Retrieval : Passed"
        )

        # Test a posting that does not exist.
        invalid_posting_id = 999999999

        try:
            get_job_posting(
                posting_id=invalid_posting_id,
                session=session,
            )

            raise RuntimeError(
                "Expected HTTPException for "
                "non-existent posting."
            )

        except HTTPException as exc:
            if exc.status_code != 404:
                raise RuntimeError(
                    "Expected status code 404, "
                    f"got {exc.status_code}."
                )

        print(
            "Invalid Posting   : 404 Passed"
        )

        print()
        print(
            "Job posting API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()