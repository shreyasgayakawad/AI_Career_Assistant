"""
Job Posting Repository

Repository for JobPosting database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.repositories.base_repository import BaseRepository


class JobPostingRepository(BaseRepository[JobPosting]):
    """
    Repository for JobPosting entities.
    """

    def __init__(self, session: Session):
        super().__init__(JobPosting, session)

    def get_by_url(
        self,
        url: str,
    ) -> JobPosting | None:
        """
        Retrieve a job posting by its posting URL.
        """

        statement = (
            select(JobPosting)
            .where(JobPosting.posting_url == url)
        )

        return self.session.scalar(statement)

    def get_by_source_and_external_id(
        self,
        source: Source,
        external_job_id: str,
    ) -> JobPosting | None:
        """
        Retrieve a job posting by source and external job ID.
        """

        statement = (
            select(JobPosting)
            .where(
                JobPosting.source_id == source.id,
                JobPosting.external_job_id == external_job_id,
            )
        )

        return self.session.scalar(statement)

    def search(
        self,
        *,
        keyword: str | None = None,
        company: Company | None = None,
        exclude_applied: bool = True,
    ) -> list[JobPosting]:
        """
        Search active job postings using optional filters.

        By default, postings that already have an application
        are excluded.
        """

        statement = (
            select(JobPosting)
            .join(JobPosting.job)
        )

        statement = statement.where(
            Job.active.is_(True),
            JobPosting.status == "ACTIVE",
        )

        if company is not None:
            statement = statement.where(
                Job.company_id == company.id,
            )

        if keyword:
            pattern = f"%{keyword}%"

            statement = statement.where(
                JobPosting.title.ilike(pattern)
                | JobPosting.description.ilike(pattern)
            )

        if exclude_applied:
            statement = statement.where(
                ~select(Application.id)
                .where(
                    Application.job_posting_id
                    == JobPosting.id,
                )
                .exists()
            )

        statement = statement.order_by(
            JobPosting.title,
        )

        return list(
            self.session.scalars(statement).all()
        )