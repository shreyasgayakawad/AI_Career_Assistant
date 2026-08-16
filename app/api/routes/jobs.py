"""
Job Routes

API endpoints for job search.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.job_schema import (
    JobDetailResponse,
    JobSummaryResponse,
)
from app.services.job_search_service import JobSearchService


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