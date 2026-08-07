"""
Job Search Service

Provides business logic for searching jobs.
"""

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.repositories.job_repository import JobRepository


class JobSearchService:
    """
    Business service for searching jobs.
    """

    def __init__(self, session: Session):
        self.job_repository = JobRepository(session)

    def get_job(
        self,
        job_id: int,
    ) -> Job | None:
        """
        Retrieve a job by ID.
        """

        return self.job_repository.get_by_id(job_id)

    def get_active_jobs(
        self,
    ) -> list[Job]:
        """
        Retrieve all active jobs.
        """

        return self.job_repository.get_active_jobs()

    def get_company_jobs(
        self,
        company: Company,
    ) -> list[Job]:
        """
        Retrieve all jobs for a company.
        """

        return self.job_repository.get_by_company(company)

    def search_jobs(
        self,
        keyword: str,
    ) -> list[Job]:
        """
        Search jobs by keyword.
        """

        return self.job_repository.search(keyword)