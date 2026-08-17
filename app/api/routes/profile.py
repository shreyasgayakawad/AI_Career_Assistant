"""
Candidate Profile Routes

API endpoints for the authenticated user's career profile.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.candidate_profile_schema import (
    CandidateProfileResponse,
    CandidateProfileUpdateRequest,
    SkillCreateRequest,
    SkillResponse,
    WorkExperienceCreateRequest,
    WorkExperienceResponse,
    EducationCreateRequest,
    EducationResponse,
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


# --- Skill routes -----------------------------------------------------

@router.post(
    "/skills",
    response_model=SkillResponse,
)
def add_skill(
    request: SkillCreateRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillResponse:
    """
    Add a single skill to the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    try:
        skill = service.add_skill(
            user_id=current_user.id,
            name=request.name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return SkillResponse.model_validate(
        skill,
    )


@router.delete(
    "/skills/{skill_id}",
    response_model=SkillResponse,
)
def remove_skill(
    skill_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillResponse:
    """
    Remove a single skill from the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    removed_skill = service.remove_skill(
        user_id=current_user.id,
        skill_id=skill_id,
    )

    if removed_skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found or does not belong to your profile.",
        )

    return SkillResponse.model_validate(
        removed_skill,
    )


# --- Work Experience routes --------------------------------------------

@router.post(
    "/work-experience",
    response_model=WorkExperienceResponse,
)
def add_work_experience(
    request: WorkExperienceCreateRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkExperienceResponse:
    """
    Add a single work experience entry to the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    try:
        experience = service.add_work_experience(
            user_id=current_user.id,
            company_name=request.company_name,
            job_title=request.job_title,
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return WorkExperienceResponse.model_validate(
        experience,
    )


@router.delete(
    "/work-experience/{experience_id}",
    response_model=WorkExperienceResponse,
)
def remove_work_experience(
    experience_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkExperienceResponse:
    """
    Remove a single work experience entry from the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    removed_experience = service.remove_work_experience(
        user_id=current_user.id,
        experience_id=experience_id,
    )

    if removed_experience is None:
        raise HTTPException(
            status_code=404,
            detail="Work experience not found or does not belong to your profile.",
        )

    return WorkExperienceResponse.model_validate(
        removed_experience,
    )


# --- Education routes ---------------------------------------------------

@router.post(
    "/education",
    response_model=EducationResponse,
)
def add_education(
    request: EducationCreateRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EducationResponse:
    """
    Add a single education entry to the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    try:
        education = service.add_education(
            user_id=current_user.id,
            institution=request.institution,
            degree=request.degree,
            field_of_study=request.field_of_study,
            start_date=request.start_date,
            end_date=request.end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return EducationResponse.model_validate(
        education,
    )


@router.delete(
    "/education/{education_id}",
    response_model=EducationResponse,
)
def remove_education(
    education_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EducationResponse:
    """
    Remove a single education entry from the authenticated user's profile.
    """

    service = CandidateProfileService(session)

    removed_education = service.remove_education(
        user_id=current_user.id,
        education_id=education_id,
    )

    if removed_education is None:
        raise HTTPException(
            status_code=404,
            detail="Education not found or does not belong to your profile.",
        )

    return EducationResponse.model_validate(
        removed_education,
    )