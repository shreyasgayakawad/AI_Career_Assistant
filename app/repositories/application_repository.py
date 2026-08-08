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
        super().__init__(
            Application,
            session,
        )

    def get_by_user_and_job_posting(
        self,
        user_id: int,
        job_posting_id: int,
    ) -> Application | None:
        """
        Retrieve an application belonging to a specific
        user and job posting.
        """

        statement = (
            select(Application)
            .where(
                Application.user_id == user_id,
                Application.job_posting_id == job_posting_id,
            )
        )

        return self.session.scalar(statement)

    def get_all_for_user(
        self,
        user_id: int,
    ) -> list[Application]:
        """
        Retrieve all applications belonging to a user.
        """

        statement = (
            select(Application)
            .where(
                Application.user_id == user_id,
            )
            .order_by(
                Application.applied_at.desc(),
            )
        )

        return list(
            self.session.scalars(statement).all()
        )