"""
Test Job Repository

Integration test for the JobRepository.
"""

# Register all SQLAlchemy models
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.job import Job
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_repository import JobRepository


def main() -> None:
    """
    Test creating and retrieving a job.
    """

    session = SessionLocal()

    try:
        company_repository = CompanyRepository(session)
        job_repository = JobRepository(session)

        company = company_repository.get_by_name("Anthropic")

        if company is None:
            raise RuntimeError(
                "Company 'Anthropic' does not exist. "
                "Run test_job_import_service first."
            )

        job = job_repository.get_by_company_and_title(
            company,
            "Software Engineer",
        )

        if job is None:
            job = Job(
                company=company,
                title="Software Engineer",
            )

            job = job_repository.create(job)
            print(f"Created Job ID : {job.id}")
        else:
            print(f"Job already exists. ID : {job.id}")

        loaded_job = job_repository.get_by_company_and_title(
            company,
            "Software Engineer",
        )

        if loaded_job:
            print(f"Retrieved Job : {loaded_job.title}")
        else:
            print("Job not found.")

    finally:
        session.close()


if __name__ == "__main__":
    main()