"""
Job Routes

API endpoints for job search.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.job_posting import JobPosting
from app.models.user import User
from app.schemas.job_schema import (
    CoverLetterDraftResponse,
    JobDetailResponse,
    JobSummaryResponse,
    MatchResultResponse,
)
from app.services.candidate_profile_service import CandidateProfileService
from app.services.job_matching_service import JobMatchingService
from app.services.job_search_service import JobSearchService
from app.services.resume_assistant_service import (
    COVER_LETTER_DRAFT_NOTE,
    ResumeAssistantService,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=list[JobSummaryResponse],
)
def get_jobs(
    keyword: str | None = None,
    company: str | None = None,
    work_mode: str | None = None,
    location: str | None = None,
    posted_after: str | None = None,
    has_salary: bool | None = None,
    employment_type: str | None = None,
    experience_level: str | None = None,
    session: Session = Depends(get_db),
) -> list[JobSummaryResponse]:
    """
    Retrieve available job postings.

    Already-applied postings are excluded.

    Work mode is an optional exact-match filter.
    Location is an optional case-insensitive partial-match filter.
    Posted-after is an optional ISO date filter (e.g. ?posted_after=2026-08-01).
    Has-salary is an optional boolean filter: true = has salary data, false = no salary data.
    Employment type is an optional exact-match filter.
    Experience level is an optional exact-match filter.
    Invalid date format returns HTTP 400.
    """

    service = JobSearchService(session)

    try:
        postings = service.search_available_postings(
            keyword=keyword,
            company_name=company,
            work_mode=work_mode,
            location=location,
            posted_after=posted_after,
            has_salary=has_salary,
            employment_type=employment_type,
            experience_level=experience_level,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return [
        JobSummaryResponse(
            id=posting.id,
            job_id=posting.job_id,
            title=posting.title,
            company=posting.job.company.name,
            location=posting.location,
            work_mode=posting.work_mode,
            posting_url=posting.posting_url,
        )
        for posting in postings
    ]


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
)
def get_job(
    job_id: int,
    session: Session = Depends(get_db),
) -> JobDetailResponse:
    """
    Retrieve a logical job by ID.
    """

    service = JobSearchService(session)

    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    posting = next(
        (
            posting
            for posting in job.postings
            if posting.status == "ACTIVE"
        ),
        None,
    )

    if posting is None:
        raise HTTPException(
            status_code=404,
            detail="No active job posting found.",
        )

    return JobDetailResponse(
        id=posting.id,
        job_id=job.id,
        title=posting.title,
        company=job.company.name,
        location=posting.location,
        work_mode=posting.work_mode,
        posting_url=posting.posting_url,
        description=posting.description,
    )


@router.get(
    "/{job_posting_id}/match-score",
    response_model=MatchResultResponse,
)
def get_job_match_score(
    job_posting_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchResultResponse:
    """
    Retrieve the match score between the current user's candidate
    profile and a specific job posting.

    The candidate profile is created automatically if this is the
    user's first interaction with their profile, matching the lazy-
    creation behavior already used by GET /profile/ and the Phase 4
    profile-writing endpoints.
    """

    job_posting = session.get(
        JobPosting,
        job_posting_id,
    )

    if job_posting is None:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found.",
        )

    profile_service = CandidateProfileService(session)
    candidate_profile = profile_service.get_or_create_profile(
        current_user.id,
    )

    matching_service = JobMatchingService()

    result = matching_service.calculate_match_score(
        candidate_profile=candidate_profile,
        job_posting=job_posting,
    )

    return MatchResultResponse(
        overall_score=result.overall_score,
        matched_skills=result.matched_skills,
        unmatched_skills=result.unmatched_skills,
        location_match=result.location_match,
        zero_skills_message=result.zero_skills_message,
    )


@router.get(
    "/{job_posting_id}/cover-letter-draft",
    response_model=CoverLetterDraftResponse,
)
def get_cover_letter_draft(
    job_posting_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CoverLetterDraftResponse:
    """
    Assemble a cover-letter draft for this posting from the current
    user's structured profile data using a fixed template.

    This is not AI-generated text: the draft is a deterministic
    fill-in of real profile data, returned with a note making clear
    it is a starting point to edit rather than a finished letter.

    The candidate profile is created automatically if this is the
    user's first interaction with their profile, matching the lazy-
    creation behavior of GET /jobs/{id}/match-score.
    """

    job_posting = session.get(
        JobPosting,
        job_posting_id,
    )

    if job_posting is None:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found.",
        )

    profile_service = CandidateProfileService(session)
    candidate_profile = profile_service.get_or_create_profile(
        current_user.id,
    )

    assistant_service = ResumeAssistantService()

    skill_emphasis = assistant_service.get_skill_emphasis(
        candidate_profile=candidate_profile,
        job_posting=job_posting,
    )

    draft_text = assistant_service.generate_cover_letter_draft(
        candidate_name=current_user.name,
        candidate_profile=candidate_profile,
        job_posting=job_posting,
        company_name=job_posting.job.company.name,
    )

    return CoverLetterDraftResponse(
        job_posting_id=job_posting.id,
        draft_text=draft_text,
        skill_emphasis=skill_emphasis,
        note=COVER_LETTER_DRAFT_NOTE,
    )