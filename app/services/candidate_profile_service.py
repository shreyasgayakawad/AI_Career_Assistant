"""
Candidate Profile Service

Provides business logic for creating and updating candidate profiles.
"""

from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.repositories.candidate_profile_repository import (
    CandidateProfileRepository,
)


class CandidateProfileService:
    """
    Business service for candidate profiles.
    """

    def __init__(self, session: Session):
        self.repository = CandidateProfileRepository(session)

    def get_profile(
        self,
        user_id: int,
    ) -> CandidateProfile | None:
        """
        Retrieve a candidate profile for a user.
        """

        return self.repository.get_by_user_id(user_id)

    def get_or_create_profile(
        self,
        user_id: int,
    ) -> CandidateProfile:
        """
        Retrieve an existing profile or create an empty one.
        """

        profile = self.repository.get_by_user_id(user_id)

        if profile is not None:
            return profile

        profile = CandidateProfile(
            user_id=user_id,
        )

        return self.repository.create(profile)

    def update_profile(
        self,
        user_id: int,
        *,
        phone: str | None,
        location: str | None,
        professional_summary: str | None,
        skills: str | None,
        experience: str | None,
        education: str | None,
    ) -> CandidateProfile:
        """
        Create or update a user's candidate profile.
        """

        profile = self.repository.get_by_user_id(user_id)

        if profile is None:
            profile = CandidateProfile(
                user_id=user_id,
            )

            profile.phone = phone
            profile.location = location
            profile.professional_summary = professional_summary
            profile.skills = skills
            profile.experience = experience
            profile.education = education

            return self.repository.create(profile)

        profile.phone = phone
        profile.location = location
        profile.professional_summary = professional_summary
        profile.skills = skills
        profile.experience = experience
        profile.education = education

        self.repository.session.commit()
        self.repository.session.refresh(profile)

        return profile