"""
Job Routes

API endpoints for job search.
"""

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.api.dependencies import get_db
from app.schemas.job_schema import JobResponse
from app.services.job_search_service import JobSearchService

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=list[JobResponse],
)
def get_jobs(
    session: Session = Depends(get_db),
) -> list[JobResponse]:
    """
    Retrieve all active jobs.
    """

    service = JobSearchService(session)

    jobs = service.get_active_jobs()

    return [
        JobResponse(
            id=job.id,
            title=job.title,
            company=job.company.name,
        )
        for job in jobs
    ]