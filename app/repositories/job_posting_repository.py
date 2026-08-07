"""
Job Posting Repository

Repository for JobPosting database operations.
"""

from sqlalchemy.orm import Session

from app.models.job_posting import JobPosting
from app.repositories.base_repository import BaseRepository


class JobPostingRepository(BaseRepository[JobPosting]):
    """
    Repository for JobPosting entities.
    """

    def __init__(self, session: Session):
        super().__init__(JobPosting, session)