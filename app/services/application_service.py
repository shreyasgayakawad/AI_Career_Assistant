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
        self.application_repository = ApplicationRepository(
            session,
        )

    def get_application_by_job_posting(
        self,
        user_id: int,
        job_posting_id: int,
    ) -> Application | None:
        """
        Retrieve a user's application for a specific
        job posting.
        """

        return (
            self.application_repository
            .get_by_user_and_job_posting(
                user_id=user_id,
                job_posting_id=job_posting_id,
            )
        )

    def has_applied(
        self,
        user_id: int,
        job_posting_id: int,
    ) -> bool:
        """
        Check whether a user has applied to a job posting.
        """

        application = (
            self.application_repository
            .get_by_user_and_job_posting(
                user_id=user_id,
                job_posting_id=job_posting_id,
            )
        )

        return application is not None

    def mark_as_applied(
        self,
        user_id: int,
        job_posting_id: int,
        resume_id: int | None = None,
    ) -> Application:
        """
        Mark a job posting as applied for a specific user.

        Raises ValueError if that user has already applied
        to the job posting.
        """

        existing_application = (
            self.application_repository
            .get_by_user_and_job_posting(
                user_id=user_id,
                job_posting_id=job_posting_id,
            )
        )

        if existing_application is not None:
            raise ValueError(
                "Job posting has already been applied to."
            )

        application = Application(
            user_id=user_id,
            job_posting_id=job_posting_id,
            resume_id=resume_id,
            applied_at=datetime.utcnow(),
        )

        return self.application_repository.create(
            application,
        )

    def update_status(
        self,
        user_id: int,
        application_id: int,
        new_status: str,
    ) -> Application | None:
        """
        Update the status of a specific application.

        Looks the application up directly by its own primary key
        (not by job_posting_id, which is a different field entirely)
        and verifies it belongs to the requesting user.

        Returns None if the application does not exist or does not
        belong to the requesting user -- matching the None-return
        convention already used by CandidateProfileService.remove_skill()
        and similar ownership-checked methods.

        Raises ValueError if new_status is not one of
        Application.ALLOWED_STATUSES.
        """

        application = self.application_repository.get_by_id(
            application_id,
        )

        if application is None or application.user_id != user_id:
            return None

        if new_status not in Application.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status: {new_status}. "
                "Allowed statuses: "
                f"{', '.join(sorted(Application.ALLOWED_STATUSES))}"
            )

        application.status = new_status

        self.application_repository.session.commit()
        self.application_repository.session.refresh(application)

        return application

    def get_all_applications(
        self,
        user_id: int,
    ) -> list[Application]:
        """
        Retrieve all applications belonging to a user.
        """

        return (
            self.application_repository
            .get_all_for_user(
                user_id=user_id,
            )
        )