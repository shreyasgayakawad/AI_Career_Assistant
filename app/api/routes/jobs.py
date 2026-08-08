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
    session: Session = Depends(get_db),
) -> list[JobSummaryResponse]:
    """
    Retrieve active jobs.

    Optionally filter by keyword.
    """

    service = JobSearchService(session)

    if keyword:
        jobs = service.search_jobs(keyword)
    else:
        jobs = service.get_active_jobs()

    return [
        JobSummaryResponse(
            id=job.id,
            title=job.title,
            company=job.company.name,
        )
        for job in jobs
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
    Retrieve a job by ID.
    """

    service = JobSearchService(session)

    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return JobDetailResponse(
        id=job.id,
        title=job.title,
        company=job.company.name,
        description=job.description,
    )