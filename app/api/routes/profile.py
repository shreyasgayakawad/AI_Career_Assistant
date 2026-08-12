"""
Candidate Profile Routes

API endpoints for the authenticated user's career profile.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.candidate_profile_schema import (
    CandidateProfileResponse,
    CandidateProfileUpdateRequest,
)
from app.services.candidate_profile_service import (
    CandidateProfileService,
)

router = APIRouter(
    prefix="/profile",
    tags=["Candidate Profile"],
)


@router.get(
    "/",
    response_model=CandidateProfileResponse,
)
def get_profile(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CandidateProfileResponse:
    """
    Retrieve the authenticated user's candidate profile.
    """

    service = CandidateProfileService(session)

    profile = service.get_or_create_profile(
        user_id=current_user.id,
    )

    return CandidateProfileResponse.model_validate(
        profile,
    )


@router.put(
    "/",
    response_model=CandidateProfileResponse,
)
def update_profile(
    profile_data: CandidateProfileUpdateRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CandidateProfileResponse:
    """
    Create or update the authenticated user's candidate profile.
    """

    service = CandidateProfileService(session)

    profile = service.update_profile(
        user_id=current_user.id,
        phone=profile_data.phone,
        location=profile_data.location,
        professional_summary=(
            profile_data.professional_summary
        ),
        skills=profile_data.skills,
        experience=profile_data.experience,
        education=profile_data.education,
    )

    return CandidateProfileResponse.model_validate(
        profile,
    )