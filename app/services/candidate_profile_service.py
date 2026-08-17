"""
Candidate Profile Service

Provides business logic for creating and updating candidate profiles.
"""

from datetime import datetime
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_work_experience import CandidateWorkExperience
from app.models.candidate_education import CandidateEducation
from app.repositories.candidate_profile_repository import (
    CandidateProfileRepository,
)
from app.repositories.candidate_skill_repository import (
    CandidateSkillRepository,
)
from app.repositories.candidate_work_experience_repository import (
    CandidateWorkExperienceRepository,
)
from app.repositories.candidate_education_repository import (
    CandidateEducationRepository,
)


class CandidateProfileService:
    """
    Business service for candidate profiles.
    """

    def __init__(self, session: Session):
        self.profile_repository = CandidateProfileRepository(session)
        self.skill_repository = CandidateSkillRepository(session)
        self.work_experience_repository = CandidateWorkExperienceRepository(
            session,
        )
        self.education_repository = CandidateEducationRepository(session)

    def get_profile(
        self,
        user_id: int,
    ) -> CandidateProfile | None:
        """
        Retrieve a candidate profile for a user.
        """

        return self.profile_repository.get_by_user_id(user_id)

    def get_or_create_profile(
        self,
        user_id: int,
    ) -> CandidateProfile:
        """
        Retrieve an existing profile or create an empty one.
        """

        profile = self.profile_repository.get_by_user_id(user_id)

        if profile is not None:
            return profile

        profile = CandidateProfile(
            user_id=user_id,
        )

        return self.profile_repository.create(profile)

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

        The free-text ``skills`` / ``experience`` / ``education`` fields
        are updated independently of the structured entries below.
        """

        profile = self.profile_repository.get_by_user_id(user_id)

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

            return self.profile_repository.create(profile)

        profile.phone = phone
        profile.location = location
        profile.professional_summary = professional_summary
        profile.skills = skills
        profile.experience = experience
        profile.education = education

        self.profile_repository.session.commit()
        self.profile_repository.session.refresh(profile)

        return profile

    # --- granular skill management -----------------------------------

    def add_skill(self, user_id: int, name: str) -> CandidateSkill:
        """
        Add a single skill to the user's profile.

        The profile is created automatically if this is the user's
        first write to their profile. If the user already has a skill
        with this name (case-insensitive), the existing entry is
        returned rather than creating a duplicate.
        """

        profile = self.get_or_create_profile(user_id)

        existing_profile_skill = next(
            (
                s
                for s in self.skill_repository.get_by_profile(profile.id)
                if s.name.lower() == name.lower()
            ),
            None,
        )

        if existing_profile_skill is not None:
            return existing_profile_skill

        skill = CandidateSkill(
            candidate_profile_id=profile.id,
            name=name,
        )

        return self.skill_repository.create(skill)

    def remove_skill(
        self,
        user_id: int,
        skill_id: int,
    ) -> SimpleNamespace | None:
        """
        Remove a single skill from the user's profile.

        Returns a snapshot of the removed skill's data, or ``None``
        if it was not found or not owned by this user's profile.

        A snapshot (rather than the ORM object itself) is returned
        because the session's default expire-on-commit behavior makes
        the original object's attributes unreadable immediately after
        the row is deleted and the transaction commits.
        """

        profile = self.profile_repository.get_by_user_id(user_id)

        if profile is None:
            return None

        skill = self.skill_repository.get_by_id(skill_id)

        if skill is None or skill.candidate_profile_id != profile.id:
            return None

        removed_snapshot = SimpleNamespace(
            id=skill.id,
            name=skill.name,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )

        self.skill_repository.session.delete(skill)
        self.skill_repository.session.commit()

        return removed_snapshot

    # --- granular work experience management --------------------------

    @staticmethod
    def _parse_date(value: str, field_name: str):
        """
        Parse an ISO date string, raising a clear ValueError on
        malformed input rather than letting a bare ValueError with
        a confusing message propagate up.
        """

        try:
            return datetime.fromisoformat(value).date()
        except ValueError as exc:
            raise ValueError(
                f"Invalid {field_name}: {value}"
            ) from exc

    def add_work_experience(
        self,
        user_id: int,
        company_name: str,
        job_title: str | None,
        start_date: str,
        end_date: str | None,
        description: str | None,
    ) -> CandidateWorkExperience:
        """
        Add a single work experience entry to the user's profile.

        ``start_date`` and ``end_date`` should be ISO date strings
        (e.g. ``"2020-01-01"``). ``end_date`` may be ``None`` for
        current / ongoing positions. The profile is created
        automatically if this is the user's first profile write.
        """

        profile = self.get_or_create_profile(user_id)

        start = self._parse_date(start_date, "start_date")
        end = (
            self._parse_date(end_date, "end_date")
            if end_date
            else None
        )

        experience = CandidateWorkExperience(
            candidate_profile_id=profile.id,
            company_name=company_name,
            job_title=job_title,
            start_date=start,
            end_date=end,
            description=description,
        )

        return self.work_experience_repository.create(experience)

    def remove_work_experience(
        self,
        user_id: int,
        experience_id: int,
    ) -> SimpleNamespace | None:
        """
        Remove a single work experience entry from the user's profile.

        Returns a snapshot of the removed entry's data, or ``None`` if
        it was not found or not owned by this user's profile. See
        ``remove_skill`` for why a snapshot is returned instead of the
        ORM object itself.
        """

        profile = self.profile_repository.get_by_user_id(user_id)

        if profile is None:
            return None

        experience = self.work_experience_repository.get_by_id(
            experience_id,
        )

        if (
            experience is None
            or experience.candidate_profile_id != profile.id
        ):
            return None

        removed_snapshot = SimpleNamespace(
            id=experience.id,
            company_name=experience.company_name,
            job_title=experience.job_title,
            start_date=experience.start_date,
            end_date=experience.end_date,
            description=experience.description,
            created_at=experience.created_at,
            updated_at=experience.updated_at,
        )

        self.work_experience_repository.session.delete(experience)
        self.work_experience_repository.session.commit()

        return removed_snapshot

    # --- granular education management ---------------------------------

    def add_education(
        self,
        user_id: int,
        institution: str,
        degree: str,
        field_of_study: str | None,
        start_date: str | None,
        end_date: str | None,
    ) -> CandidateEducation:
        """
        Add a single education entry to the user's profile.

        ``start_date`` and ``end_date`` should be ISO date strings
        (e.g. ``"2015-09-01"``). Either may be ``None``. The profile
        is created automatically if this is the user's first profile
        write.
        """

        profile = self.get_or_create_profile(user_id)

        start = (
            self._parse_date(start_date, "start_date")
            if start_date
            else None
        )
        end = (
            self._parse_date(end_date, "end_date")
            if end_date
            else None
        )

        education = CandidateEducation(
            candidate_profile_id=profile.id,
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            start_date=start,
            end_date=end,
        )

        return self.education_repository.create(education)

    def remove_education(
        self,
        user_id: int,
        education_id: int,
    ) -> SimpleNamespace | None:
        """
        Remove a single education entry from the user's profile.

        Returns a snapshot of the removed entry's data, or ``None`` if
        it was not found or not owned by this user's profile. See
        ``remove_skill`` for why a snapshot is returned instead of the
        ORM object itself.
        """

        profile = self.profile_repository.get_by_user_id(user_id)

        if profile is None:
            return None

        education = self.education_repository.get_by_id(education_id)

        if education is None or education.candidate_profile_id != profile.id:
            return None

        removed_snapshot = SimpleNamespace(
            id=education.id,
            institution=education.institution,
            degree=education.degree,
            field_of_study=education.field_of_study,
            start_date=education.start_date,
            end_date=education.end_date,
            created_at=education.created_at,
            updated_at=education.updated_at,
        )

        self.education_repository.session.delete(education)
        self.education_repository.session.commit()

        return removed_snapshot