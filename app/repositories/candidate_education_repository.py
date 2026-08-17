"""
Candidate Education Repository

Repository for CandidateEducation database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository

from app.models.candidate_education import CandidateEducation


class CandidateEducationRepository(BaseRepository[CandidateEducation]):
    """
    Repository for CandidateEducation entities.
    """

    def __init__(self, session: Session):
        super().__init__(CandidateEducation, session)

    def get_by_profile(self, candidate_profile_id: int) -> list[CandidateEducation]:
        """
        Retrieve all education entries for a candidate profile.
        """

        statement = select(CandidateEducation).where(
            CandidateEducation.candidate_profile_id == candidate_profile_id,
        )

        return list(self.session.scalars(statement).all())

    def get_degrees(self, candidate_profile_id: int) -> list[CandidateEducation]:
        """
        Retrieve education entries grouped by degree type.
        """

        statement = select(CandidateEducation).where(
            CandidateEducation.candidate_profile_id == candidate_profile_id,
        )

        return list(self.session.scalars(statement).all())


def get_candidate_education_repository(session: Session) -> CandidateEducationRepository:
    """
    Factory function to get a CandidateEducationRepository instance.
    """

    return CandidateEducationRepository(session)