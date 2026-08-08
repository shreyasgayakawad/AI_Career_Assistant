"""
Test Application Repository

Integration test for ApplicationRepository.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.repositories.application_repository import ApplicationRepository


def main() -> None:
    """
    Test creating and retrieving an application.
    """

    session = SessionLocal()

    try:
        application_repository = ApplicationRepository(session)

        posting = session.query(JobPosting).first()

        if posting is None:
            raise RuntimeError(
                "No job posting exists. "
                "Run the Greenhouse import first."
            )

        print("=" * 50)
        print("Application Repository Test")
        print("=" * 50)

        print(f"Job Posting ID : {posting.id}")
        print(f"Job Title      : {posting.title}")
        print(f"Posting URL    : {posting.posting_url}")

        existing_application = (
            application_repository.get_by_job_posting_id(
                posting.id,
            )
        )

        if existing_application is None:
            application = Application(
                job_posting=posting,
            )

            application = application_repository.create(
                application,
            )

            print()
            print(f"Created Application ID : {application.id}")
        else:
            application = existing_application

            print()
            print(
                "Application already exists. "
                f"ID : {application.id}"
            )

        loaded_application = (
            application_repository.get_by_job_posting_id(
                posting.id,
            )
        )

        if loaded_application is None:
            raise RuntimeError(
                "Application could not be retrieved."
            )

        print()
        print(
            "Retrieved Application ID : "
            f"{loaded_application.id}"
        )

        applications = application_repository.get_all()

        print()
        print(
            f"Total Applications       : "
            f"{len(applications)}"
        )

        print()
        print("Application repository test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()