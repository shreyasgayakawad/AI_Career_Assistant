"""
Job Posting Repository

Repository for JobPosting database operations.
"""

from datetime import datetime

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
        work_mode: str | None = None,
        location: str | None = None,
        posted_after: datetime | None = None,
        has_salary: bool | None = None,
        employment_type: str | None = None,
        experience_level: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        exclude_applied: bool = True,
    ) -> list[JobPosting]:
        """
        Search active job postings using optional filters.

        By default, postings that already have an application
        are excluded.

        Keyword is split on whitespace; every token must appear
        (case-insensitively) in the posting's title or description,
        with tokens allowed to match different fields and in any
        order.
        Work mode filtering uses exact matching.
        Location filtering uses case-insensitive partial match.
        Posted-after filtering uses ISO date string (e.g. ?posted_after=2026-08-01).
        Has-salary filtering: True = postings with salary data, False = without.
        Salary range filtering:
          - salary_min: show jobs that could pay at least X (filters on salary_max >= X)
          - salary_max: show jobs with minimum <= Y (filters on salary_min <= Y)
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

        if work_mode is not None:
            statement = statement.where(
                JobPosting.work_mode == work_mode,
            )

        if location:
            statement = statement.where(
                JobPosting.location.ilike(f"%{location}%"),
            )

        if posted_after:
            statement = statement.where(
                JobPosting.posted_date >= posted_after,
            )

        if has_salary is not None:
            if has_salary:
                statement = statement.where(
                    JobPosting.salary.isnot(None),
                )
            else:
                statement = statement.where(
                    JobPosting.salary.is_(None),
                )

        if salary_min is not None:
            # "Show jobs that could pay at least X"
            # i.e. the posting's maximum stated salary should clear the bar
            statement = statement.where(
                JobPosting.salary_max >= salary_min,
            )

        if salary_max is not None:
            # "Show jobs with minimum within range"
            # i.e. the posting's minimum stated salary should be at most Y
            statement = statement.where(
                JobPosting.salary_min <= salary_max,
            )

        if employment_type is not None:
            statement = statement.where(
                Job.employment_type == employment_type,
            )

        if experience_level is not None:
            statement = statement.where(
                Job.experience_level == experience_level,
            )

        if keyword:
            # Multi-keyword AND semantics: every whitespace-separated
            # token must appear in the title or description. Tokens
            # may match different fields and in any order, so a search
            # for "cloud support" also finds a posting titled
            # "Support Engineer - Cloud Platform".
            for token in keyword.split():
                pattern = f"%{token}%"

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