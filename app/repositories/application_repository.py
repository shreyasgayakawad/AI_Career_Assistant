"""
Application Repository

Repository for Application database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """
    Repository for Application entities.
    """

    def __init__(self, session: Session):
        super().__init__(Application, session)

    def get_by_job_posting_id(
        self,
        job_posting_id: int,
    ) -> Application | None:
        """
        Retrieve an application by job posting ID.
        """

        statement = (
            select(Application)
            .where(
                Application.job_posting_id == job_posting_id,
            )
        )

        return self.session.scalar(statement)

    def get_all(self) -> list[Application]:
        """
        Retrieve all applications.
        """

        statement = (
            select(Application)
            .order_by(Application.applied_at.desc())
        )

        return list(
            self.session.scalars(statement).all()
        )