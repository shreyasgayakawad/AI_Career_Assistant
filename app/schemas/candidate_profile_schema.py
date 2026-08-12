"""
Candidate Profile Schemas

Pydantic models for candidate profile API requests and responses.
"""

from pydantic import BaseModel, ConfigDict


class CandidateProfileResponse(BaseModel):
    """
    Candidate profile returned to the client.
    """

    id: int
    user_id: int
    phone: str | None
    location: str | None
    professional_summary: str | None
    skills: str | None
    experience: str | None
    education: str | None

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