"""
Application Routes

API endpoints for tracking job applications.
"""

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_db
from app.models.job_posting import JobPosting
from app.services.application_service import ApplicationService


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.post(
    "/{job_posting_id}",
    status_code=status.HTTP_201_CREATED,
)
def mark_job_as_applied(
    job_posting_id: int,
    session: Session = Depends(get_db),
) -> dict[str, int | str]:
    """
    Mark a specific job posting as applied.
    """

    job_posting = session.get(
        JobPosting,
        job_posting_id,
    )

    if job_posting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found.",
        )

    service = ApplicationService(session)

    application = service.mark_as_applied(
        job_posting_id=job_posting_id,
    )

    return {
        "id": application.id,
        "job_posting_id": application.job_posting_id,
        "message": "Job posting marked as applied.",
    }


@router.get(
    "/",
)
def get_applications(
    session: Session = Depends(get_db),
) -> list[dict[str, object]]:
    """
    Retrieve all job applications.
    """

    service = ApplicationService(session)

    applications = service.get_all_applications()

    return [
        {
            "id": application.id,
            "job_posting_id": application.job_posting_id,
            "applied_at": application.applied_at,
        }
        for application in applications
    ]