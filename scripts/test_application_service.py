"""
Test Application Service

Integration test for ApplicationService.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.services.application_service import ApplicationService


def main() -> None:
    """
    Test ApplicationService business methods.
    """

    session = SessionLocal()

    try:
        service = ApplicationService(session)

        posting = session.query(JobPosting).first()

        if posting is None:
            raise RuntimeError(
                "No job posting exists. "
                "Run the Greenhouse import first."
            )

        print("=" * 50)
        print("Application Service Test")
        print("=" * 50)

        print(f"Job Posting ID : {posting.id}")
        print(f"Job Title      : {posting.title}")

        application = service.get_application_by_job_posting(
            posting.id,
        )

        if application is None:
            application = service.mark_as_applied(
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
            posting.id,
        )

        if not has_applied:
            raise RuntimeError(
                "has_applied() returned False "
                "for an existing application."
            )

        print()
        print("Has Applied             : True")

        application_again = service.mark_as_applied(
            job_posting_id=posting.id,
        )

        if application_again.id != application.id:
            raise RuntimeError(
                "Duplicate application was created."
            )

        applications = service.get_all_applications()

        if len(applications) != 1:
            raise RuntimeError(
                "Expected exactly 1 application, "
                f"found {len(applications)}."
            )

        print(
            "Duplicate Prevention    : Passed"
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