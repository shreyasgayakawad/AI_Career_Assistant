"""
Job Import Service

Imports scraped jobs into the database.
"""

from sqlalchemy.orm import Session

from app.dto.scraped_job import ScrapedJob
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_posting_repository import (
    JobPostingRepository,
)
from app.repositories.job_repository import JobRepository
from app.repositories.source_repository import SourceRepository
from app.services.salary_parser import parse_salary_text


class JobImportService:
    """
    Imports ScrapedJob objects into the database.
    """

    def __init__(self, session: Session):
        self.session = session

        self.company_repository = CompanyRepository(
            session,
        )
        self.job_repository = JobRepository(
            session,
        )
        self.job_posting_repository = (
            JobPostingRepository(session)
        )
        self.source_repository = SourceRepository(
            session,
        )

    def get_or_create_company(
        self,
        company_name: str,
    ) -> Company:
        """
        Retrieve an existing company or create a new one.
        """

        company = self.company_repository.get_by_name(
            company_name,
        )

        if company is not None:
            return company

        company = Company(
            name=company_name,
        )

        return self.company_repository.create(
            company,
        )

    def get_or_create_job(
        self,
        title: str,
        company: Company,
        employment_type: str | None = None,
        experience_level: str | None = None,
    ) -> Job:
        """
        Retrieve an existing job or create a new one.

        If the job is newly created, the supplied
        ``employment_type`` and ``experience_level`` are set
        once and never overwritten by later imports.
        """

        job = self.job_repository.get_by_company_and_title(
            company,
            title,
        )

        if job is not None:
            return job

        job = Job(
            title=title,
            company=company,
        )

        if employment_type is not None:
            job.employment_type = employment_type

        if experience_level is not None:
            job.experience_level = experience_level

        return self.job_repository.create(
            job,
        )

    def get_source(
        self,
        source_name: str,
    ) -> Source:
        """
        Retrieve an existing source.
        """

        source = self.source_repository.get_by_name(
            source_name,
        )

        if source is None:
            raise ValueError(
                f"Source '{source_name}' does not exist."
            )

        return source

    def job_posting_exists(
        self,
        *,
        url: str,
        source: Source,
        external_job_id: str | None = None,
    ) -> bool:
        """
        Check whether a job posting already exists.

        A posting is considered a duplicate when its URL already
        exists or, when available, its source/external ID already
        exists.
        """

        if self.job_posting_repository.get_by_url(
            url,
        ) is not None:
            return True

        if external_job_id:
            return (
                self.job_posting_repository
                .get_by_source_and_external_id(
                    source=source,
                    external_job_id=external_job_id,
                )
                is not None
            )

        return False

    def create_job_posting(
        self,
        *,
        job: Job,
        source: Source,
        title: str,
        posting_url: str,
        location: str | None = None,
        work_mode: str | None = None,
        description: str | None = None,
        external_job_id: str | None = None,
        salary: str | None = None,
        posted_date=None,
    ) -> JobPosting:
        """
        Create a JobPosting entity.

        Parses the salary text into numeric min/max bounds using the salary parser.
        If the salary text cannot be parsed, salary_min/salary_max remain None.
        """
        min_salary, max_salary = parse_salary_text(salary) if salary else (None, None)

        posting = JobPosting(
            job=job,
            source=source,
            title=title,
            posting_url=posting_url,
            location=location,
            work_mode=work_mode or "UNKNOWN",
            description=description,
            external_job_id=external_job_id,
            salary=salary,
            salary_min=min_salary,
            salary_max=max_salary,
            posted_date=posted_date,
        )

        return self.job_posting_repository.create(
            posting,
        )

    def import_job(
        self,
        scraped_job: ScrapedJob,
        source_name: str,
    ) -> JobPosting | None:
        """
        Import a single scraped job.
        """

        source = self.get_source(
            source_name,
        )

        if self.job_posting_exists(
            url=scraped_job.url,
            source=source,
            external_job_id=scraped_job.external_job_id,
        ):
            return None

        company = self.get_or_create_company(
            scraped_job.company,
        )

        job = self.get_or_create_job(
            title=scraped_job.title,
            company=company,
            employment_type=scraped_job.employment_type,
            experience_level=scraped_job.experience_level,
        )

        return self.create_job_posting(
            job=job,
            source=source,
            title=scraped_job.title,
            posting_url=scraped_job.url,
            location=scraped_job.location,
            work_mode=scraped_job.work_mode,
            description=scraped_job.description,
            external_job_id=scraped_job.external_job_id,
            salary=scraped_job.salary,
            posted_date=scraped_job.posted_date,
        )

    def import_jobs(
        self,
        scraped_jobs: list[ScrapedJob],
        source_name: str,
    ) -> tuple[int, int]:
        """
        Import multiple scraped jobs.

        Returns:
            (imported_count, skipped_count)
        """

        imported = 0
        skipped = 0

        for scraped_job in scraped_jobs:
            posting = self.import_job(
                scraped_job=scraped_job,
                source_name=source_name,
            )

            if posting is None:
                skipped += 1
            else:
                imported += 1

        return imported, skipped