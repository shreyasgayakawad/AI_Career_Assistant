"""
Candidate Work Experience Repository

Repository for CandidateWorkExperience database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository

from app.models.candidate_work_experience import CandidateWorkExperience


class CandidateWorkExperienceRepository(BaseRepository[CandidateWorkExperience]):
    """
    Repository for CandidateWorkExperience entities.
    """

    def __init__(self, session: Session):
        super().__init__(CandidateWorkExperience, session)

    def get_by_profile(self, candidate_profile_id: int) -> list[CandidateWorkExperience]:
        """
        Retrieve all work experiences for a candidate profile.
        """

        statement = select(CandidateWorkExperience).where(
            CandidateWorkExperience.candidate_profile_id == candidate_profile_id,
        )

        return list(self.session.scalars(statement).all())

    def get_active(self, candidate_profile_id: int) -> list[CandidateWorkExperience]:
        """
        Retrieve work experiences that are currently ongoing (end_date is None).
        """

        statement = select(CandidateWorkExperience).where(
            CandidateWorkExperience.candidate_profile_id == candidate_profile_id,
            CandidateWorkExperience.end_date.is_(None),
        )

        return list(self.session.scalars(statement).all())


def get_candidate_work_experience_repository(session: Session) -> CandidateWorkExperienceRepository:
    """
    Factory function to get a CandidateWorkExperienceRepository instance.
    """

    return CandidateWorkExperienceRepository(session)