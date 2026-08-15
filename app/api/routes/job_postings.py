"""
Job Posting Routes

API endpoints for individual job postings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.job_posting import JobPosting
from app.schemas.job_schema import JobDetailResponse


router = APIRouter(
    prefix="/job-postings",
    tags=["Job Postings"],
)


@router.get(
    "/{posting_id}",
    response_model=JobDetailResponse,
)
def get_job_posting(
    posting_id: int,
    session: Session = Depends(get_db),
) -> JobDetailResponse:
    """
    Retrieve a specific job posting by ID.
    """

    posting = session.get(
        JobPosting,
        posting_id,
    )

    if posting is None:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found.",
        )

    return JobDetailResponse(
        id=posting.id,
        job_id=posting.job_id,
        title=posting.title,
        company=posting.job.company.name,
        location=posting.location,
        work_mode=posting.work_mode,
        posting_url=posting.posting_url,
        description=posting.description,
    )