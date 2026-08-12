"""
Candidate Profile Repository

Repository for CandidateProfile database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.repositories.base_repository import BaseRepository


class CandidateProfileRepository(BaseRepository[CandidateProfile]):
    """
    Repository for CandidateProfile entities.
    """

    def __init__(self, session: Session):
        super().__init__(CandidateProfile, session)

    def get_by_user_id(
        self,
        user_id: int,
    ) -> CandidateProfile | None:
        """
        Retrieve a candidate profile by user ID.
        """

        statement = (
            select(CandidateProfile)
            .where(
                CandidateProfile.user_id == user_id,
            )
        )

        return self.session.scalar(statement)