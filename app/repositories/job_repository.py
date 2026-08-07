"""
Job Repository

Repository for Job database operations.
"""

from sqlalchemy import select
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