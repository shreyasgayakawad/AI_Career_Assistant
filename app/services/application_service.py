"""
Application Service

Provides business logic for tracking job applications.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository


class ApplicationService:
    """
    Business service for job applications.
    """

    def __init__(self, session: Session):
        self.application_repository = ApplicationRepository(session)

    def get_application_by_job_posting(
        self,
        job_posting_id: int,
    ) -> Application | None:
        """
        Retrieve an application for a specific job posting.
        """

        return self.application_repository.get_by_job_posting_id(
            job_posting_id,
        )

    def has_applied(
        self,
        job_posting_id: int,
    ) -> bool:
        """
        Check whether the user has applied to a job posting.
        """

        application = (
            self.application_repository.get_by_job_posting_id(
                job_posting_id,
            )
        )

        return application is not None

    def mark_as_applied(
        self,
        job_posting_id: int,
        resume_id: int | None = None,
    ) -> Application:
        """
        Mark a job posting as applied.

        If an application already exists, return the existing
        application instead of creating a duplicate.
        """

        existing_application = (
            self.application_repository.get_by_job_posting_id(
                job_posting_id,
            )
        )

        if existing_application is not None:
            return existing_application

        application = Application(
            job_posting_id=job_posting_id,
            resume_id=resume_id,
            applied_at=datetime.utcnow(),
        )

        return self.application_repository.create(
            application,
        )

    def get_all_applications(
        self,
    ) -> list[Application]:
        """
        Retrieve all applications.
        """

        return self.application_repository.get_all()