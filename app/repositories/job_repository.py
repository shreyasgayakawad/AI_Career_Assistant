"""
Job Repository

Repository for Job database operations.
"""

from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository[Job]):
    """
    Repository for Job entities.
    """

    def __init__(self, session: Session):
        super().__init__(Job, session)