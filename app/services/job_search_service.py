"""
Job Search Service

Provides business logic for searching jobs and job postings.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.job_repository import JobRepository


class JobSearchService:
    """
    Business service for searching jobs and job postings.
    """

    ALLOWED_WORK_MODES = {
        "REMOTE",
        "HYBRID",
        "ONSITE",
        "UNKNOWN",
    }

    def __init__(self, session: Session):
        self.job_repository = JobRepository(session)
        self.job_posting_repository = JobPostingRepository(session)
        self.company_repository = CompanyRepository(session)

    def get_job(
        self,
        job_id: int,
    ) -> Job | None:
        """
        Retrieve a logical job by ID.
        """

        return self.job_repository.get_by_id(job_id)

    def get_active_jobs(
        self,
    ) -> list[Job]:
        """
        Retrieve all active logical jobs.
        """

        return self.search_jobs()

    def get_company_jobs(
        self,
        company: Company,
    ) -> list[Job]:
        """
        Retrieve all jobs for a company.
        """

        return self.job_repository.search(
            company=company,
        )

    def search_jobs(
        self,
        *,
        keyword: str | None = None,
        company_name: str | None = None,
    ) -> list[Job]:
        """
        Search logical jobs using optional filters.
        """

        company: Company | None = None

        if company_name:
            company = self.company_repository.get_by_name(
                company_name,
            )

            if company is None:
                return []

        return self.job_repository.search(
            keyword=keyword,
            company=company,
        )

    def search_available_postings(
        self,
        *,
        keyword: str | None = None,
        company_name: str | None = None,
        work_mode: str | None = None,
        location: str | None = None,
        posted_after: str | None = None,
        has_salary: bool | None = None,
        employment_type: str | None = None,
        experience_level: str | None = None,
    ) -> list[JobPosting]:
        """
        Search active job postings that have not been applied to.

        Work mode is an optional exact-match filter.
        Location is an optional case-insensitive partial-match filter.
        Posted-after is an optional ISO date filter (e.g. ?posted_after=2026-08-01).
        Has-salary is an optional bool filter: True = has salary data, False = no salary data.
        Employment type is an optional exact-match filter on the logical job.
        Experience level is an optional exact-match filter on the logical job.
        """

        company: Company | None = None

        if company_name:
            company = self.company_repository.get_by_name(
                company_name,
            )

            if company is None:
                return []

        if work_mode is not None:
            work_mode = work_mode.strip().upper()

            if work_mode not in self.ALLOWED_WORK_MODES:
                raise ValueError(
                    f"Invalid work mode: {work_mode}"
                )

        if posted_after is not None:
            try:
                posted_after = datetime.fromisoformat(posted_after)
            except ValueError:
                raise ValueError(
                    f"Invalid posted_after date: {posted_after}"
                )

        return self.job_posting_repository.search(
            keyword=keyword,
            company=company,
            work_mode=work_mode,
            location=location,
            posted_after=posted_after,
            has_salary=has_salary,
            employment_type=employment_type,
            experience_level=experience_level,
            exclude_applied=True,
        )