"""
Job Repository

Repository for Job database operations.
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository[Job]):
    """
    Repository for Job entities.
    """

    def __init__(self, session: Session):
        super().__init__(Job, session)

    def get_by_company_and_title(
        self,
        company: Company,
        title: str,
    ) -> Job | None:
        """
        Retrieve a job by company and title.
        """

        statement = (
            select(Job)
            .where(
                Job.company_id == company.id,
                Job.title == title,
            )
        )

        return self.session.scalar(statement)

    def get_by_company(
        self,
        company: Company,
    ) -> list[Job]:
        """
        Retrieve all jobs for a company.
        """

        statement = (
            select(Job)
            .where(Job.company_id == company.id)
            .order_by(Job.title)
        )

        return list(self.session.scalars(statement).all())

    def search(
        self,
        *,
        keyword: str | None = None,
        company: Company | None = None,
        active_only: bool = True,
    ) -> list[Job]:
        """
        Search jobs using optional filters.
        """

        statement = select(Job)

        if active_only:
            statement = statement.where(Job.active.is_(True))

        if company is not None:
            statement = statement.where(
                Job.company_id == company.id,
            )

        if keyword:
            pattern = f"%{keyword}%"

            statement = statement.where(
                or_(
                    Job.title.ilike(pattern),
                    Job.description.ilike(pattern),
                )
            )

        statement = statement.order_by(Job.title)

        return list(self.session.scalars(statement).all())

    def get_active_jobs(self) -> list[Job]:
        """
        Retrieve all active jobs.
        """

        return self.search()