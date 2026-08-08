"""
Job Routes

API endpoints for job search.
"""

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

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
    session: Session = Depends(get_db),
) -> list[JobSummaryResponse]:
    """
    Retrieve available job postings.

    Already-applied postings are excluded.
    """

    service = JobSearchService(session)

    postings = service.search_available_postings(
        keyword=keyword,
        company_name=company,
    )

    return [
        JobSummaryResponse(
            id=posting.id,
            job_id=posting.job_id,
            title=posting.title,
            company=posting.job.company.name,
            location=posting.location,
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
        posting_url=posting.posting_url,
        description=posting.description,
    )