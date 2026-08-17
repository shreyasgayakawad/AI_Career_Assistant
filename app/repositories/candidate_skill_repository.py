"""
Candidate Skill Repository

Repository for CandidateSkill database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository

from app.models.candidate_skill import CandidateSkill


class CandidateSkillRepository(BaseRepository[CandidateSkill]):
    """
    Repository for CandidateSkill entities.
    """

    def __init__(self, session: Session):
        super().__init__(CandidateSkill, session)

    def get_by_profile(self, candidate_profile_id: int) -> list[CandidateSkill]:
        """
        Retrieve all skills for a candidate profile.
        """

        statement = select(CandidateSkill).where(
            CandidateSkill.candidate_profile_id == candidate_profile_id,
        )

        return list(self.session.scalars(statement).all())

    def get_by_name(self, name: str) -> CandidateSkill | None:
        """
        Retrieve a skill by name (case-insensitive).
        """

        statement = select(CandidateSkill).where(
            CandidateSkill.name.ilike(name),
        )

        return self.session.scalar(statement)


def get_candidate_skill_repository(session: Session) -> CandidateSkillRepository:
    """
    Factory function to get a CandidateSkillRepository instance.
    """

    return CandidateSkillRepository(session)