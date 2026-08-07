"""
Job Import Service

Imports scraped jobs into the database.
"""

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.models.source import Source
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.job_repository import JobRepository
from app.repositories.source_repository import SourceRepository


class JobImportService:
    """
    Imports ScrapedJob objects into the database.
    """

    def __init__(self, session: Session):
        self.session = session

        self.company_repository = CompanyRepository(session)
        self.job_repository = JobRepository(session)
        self.job_posting_repository = JobPostingRepository(session)
        self.source_repository = SourceRepository(session)

    def get_or_create_company(
        self,
        company_name: str,
    ) -> Company:
        """
        Retrieve an existing company or create a new one.
        """

        company = self.company_repository.get_by_name(company_name)

        if company is not None:
            return company

        company = Company(
            name=company_name,
        )

        return self.company_repository.create(company)

    def get_source(
        self,
        source_name: str,
    ) -> Source:
        """
        Retrieve an existing source.
        """

        source = self.source_repository.get_by_name(source_name)

        if source is None:
            raise ValueError(
                f"Source '{source_name}' does not exist."
            )

        return source

    def job_posting_exists(
        self,
        url: str,
    ) -> bool:
        """
        Check whether a job posting already exists.
        """

        posting = self.job_posting_repository.get_by_url(url)

        return posting is not None

    def create_job(
        self,
        title: str,
        company: Company,
    ) -> Job:
        """
        Create a Job entity.
        """

        job = Job(
            title=title,
            company=company,
        )

        return self.job_repository.create(job)