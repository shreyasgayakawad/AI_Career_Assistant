"""
Candidate Profile Schemas

Pydantic models for candidate profile API requests and responses.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    """
    A skill returned to the client.
    """

    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillCreateRequest(BaseModel):
    """
    Fields required to create a skill.
    """

    name: str


class WorkExperienceResponse(BaseModel):
    """
    A work experience entry returned to the client.
    """

    id: int
    company_name: str
    job_title: str | None
    start_date: date
    end_date: date | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkExperienceCreateRequest(BaseModel):
    """
    Fields required to create a work experience entry.
    """

    company_name: str
    job_title: str | None = None
    start_date: str
    end_date: str | None = None
    description: str | None = None


class EducationResponse(BaseModel):
    """
    An education entry returned to the client.
    """

    id: int
    institution: str
    degree: str
    field_of_study: str | None
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EducationCreateRequest(BaseModel):
    """
    Fields required to create an education entry.
    """

    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class CandidateProfileResponse(BaseModel):
    """
    Candidate profile returned to the client.

    Includes both the original free-text fields and the structured
    Phase 4 entries. The free-text fields are kept for backward
    compatibility; the structured lists are the new source of truth
    going forward.
    """

    id: int
    user_id: int
    phone: str | None
    location: str | None
    professional_summary: str | None
    skills: str | None
    experience: str | None
    education: str | None

    skills_list: list[SkillResponse]
    work_experiences: list[WorkExperienceResponse]
    education_entries: list[EducationResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class CandidateProfileUpdateRequest(BaseModel):
    """
    Candidate profile fields accepted when updating a profile.
    """

    phone: str | None = None
    location: str | None = None
    professional_summary: str | None = None
    skills: str | None = None
    experience: str | None = None
    education: str | None = None