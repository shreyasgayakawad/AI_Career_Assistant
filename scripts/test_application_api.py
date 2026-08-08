"""
Test Application API

Integration test for the application API route.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.applications import mark_job_as_applied
from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting


def main() -> None:
    """
    Test the mark-as-applied API route.
    """

    session = SessionLocal()

    try:
        posting = session.query(JobPosting).first()

        if posting is None:
            raise RuntimeError(
                "No job posting exists. "
                "Run the Greenhouse import first."
            )

        print("=" * 50)
        print("Application API Test")
        print("=" * 50)

        print(f"Job Posting ID : {posting.id}")
        print(f"Job Title      : {posting.title}")

        existing_application = (
            session.query(Application)
            .filter(
                Application.job_posting_id == posting.id,
            )
            .first()
        )

        application = mark_job_as_applied(
            job_posting_id=posting.id,
            session=session,
        )

        print()
        print(
            f"Application ID : {application['id']}"
        )
        print(
            f"Job Posting ID : "
            f"{application['job_posting_id']}"
        )
        print(
            f"Message        : "
            f"{application['message']}"
        )

        if existing_application is None:
            if application["id"] != 1:
                raise RuntimeError(
                    "Unexpected application ID."
                )

        application_count = (
            session.query(Application)
            .filter(
                Application.job_posting_id == posting.id,
            )
            .count()
        )

        if application_count != 1:
            raise RuntimeError(
                "Expected exactly one application "
                f"for posting {posting.id}, "
                f"found {application_count}."
            )

        second_application = mark_job_as_applied(
            job_posting_id=posting.id,
            session=session,
        )

        if second_application["id"] != application["id"]:
            raise RuntimeError(
                "Duplicate application was created."
            )

        print()
        print(
            "Duplicate Prevention : Passed"
        )

        invalid_posting_id = 999999999

        try:
            mark_job_as_applied(
                job_posting_id=invalid_posting_id,
                session=session,
            )

            raise RuntimeError(
                "Expected HTTPException for "
                "non-existent job posting."
            )

        except HTTPException as exc:
            if exc.status_code != 404:
                raise RuntimeError(
                    "Expected status code 404, "
                    f"got {exc.status_code}."
                )

            print(
                "Invalid Posting       : "
                "404 Passed"
            )

        print()
        print("Application API test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()