"""
Test Get Applications API

Integration test for retrieving all applications for an authenticated user.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.api.routes.applications import (
    get_applications,
    mark_job_as_applied,
)
from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.models.user import User


def main() -> None:
    """
    Test retrieving all applications through the API route.
    """

    session = SessionLocal()

    try:
        print("=" * 50)
        print("Get Applications API Test")
        print("=" * 50)

        # ---------------------------------------------------------
        # Ensure test user and job posting exist
        # ---------------------------------------------------------
        test_email = "test_get_applications@example.com"
        user = session.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                name="Test Get Applications User",
                email=test_email,
                password_hash="test_hash",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        posting = (
            session.query(JobPosting)
            .order_by(JobPosting.id)
            .first()
        )
        if posting is None:
            raise RuntimeError("No job postings found in database.")

        # Ensure user has applied to posting
        existing_app = (
            session.query(Application)
            .filter(
                Application.user_id == user.id,
                Application.job_posting_id == posting.id,
            )
            .first()
        )
        if not existing_app:
            mark_job_as_applied(
                job_posting_id=posting.id,
                session=session,
                current_user=user,
            )

        applications = get_applications(
            session=session,
            current_user=user,
        )

        print()
        print(
            f"Total Applications : "
            f"{len(applications)}"
        )

        for application in applications:
            print()
            print(
                f"Application ID : "
                f"{application['id']}"
            )
            print(
                f"Job Posting ID : "
                f"{application['job_posting_id']}"
            )
            print(
                f"Applied At     : "
                f"{application['applied_at']}"
            )

        if not applications:
            raise RuntimeError(
                "Expected at least one application."
            )

        print()
        print("Get applications API test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()