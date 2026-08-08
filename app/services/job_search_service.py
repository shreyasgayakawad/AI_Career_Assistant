"""
Job Search Service

Provides business logic for searching jobs and job postings.
"""

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
    ) -> list[JobPosting]:
        """
        Search active job postings that have not been applied to.
        """

        company: Company | None = None

        if company_name:
            company = self.company_repository.get_by_name(
                company_name,
            )

            if company is None:
                return []

        return self.job_posting_repository.search(
            keyword=keyword,
            company=company,
            exclude_applied=True,
        )