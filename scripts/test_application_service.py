"""
Test Application Service

Integration test for ApplicationService.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.models.user import User
from app.services.application_service import ApplicationService


def main() -> None:
    """
    Test ApplicationService business methods with user context.
    """

    session = SessionLocal()

    try:
        service = ApplicationService(session)

        # Ensure a test user exists
        test_email = "test_app_service@example.com"
        user = session.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                name="Test App Service User",
                email=test_email,
                password_hash="test_hash",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        posting = session.query(JobPosting).first()

        if posting is None:
            raise RuntimeError(
                "No job posting exists. "
                "Run the Greenhouse import first."
            )

        print("=" * 50)
        print("Application Service Test")
        print("=" * 50)

        print(f"User ID        : {user.id}")
        print(f"Job Posting ID : {posting.id}")
        print(f"Job Title      : {posting.title}")

        # Clean up any existing application for this test user/posting
        existing = (
            session.query(Application)
            .filter(
                Application.user_id == user.id,
                Application.job_posting_id == posting.id,
            )
            .first()
        )
        if existing:
            session.delete(existing)
            session.commit()

        application = service.get_application_by_job_posting(
            user_id=user.id,
            job_posting_id=posting.id,
        )

        if application is None:
            application = service.mark_as_applied(
                user_id=user.id,
                job_posting_id=posting.id,
            )

            print()
            print(
                f"Created Application ID : "
                f"{application.id}"
            )
        else:
            print()
            print(
                "Application already exists. "
                f"ID : {application.id}"
            )

        has_applied = service.has_applied(
            user_id=user.id,
            job_posting_id=posting.id,
        )

        if not has_applied:
            raise RuntimeError(
                "has_applied() returned False "
                "for an existing application."
            )

        print()
        print("Has Applied             : True")

        # Duplicate application prevention check
        try:
            service.mark_as_applied(
                user_id=user.id,
                job_posting_id=posting.id,
            )
            raise RuntimeError(
                "Duplicate application was allowed."
            )
        except ValueError:
            print("Duplicate Prevention    : Passed")

        applications = service.get_all_applications(
            user_id=user.id,
        )

        if len(applications) != 1:
            raise RuntimeError(
                "Expected exactly 1 application, "
                f"found {len(applications)}."
            )

        print(
            f"Total Applications      : "
            f"{len(applications)}"
        )

        print()
        print("Application service test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()