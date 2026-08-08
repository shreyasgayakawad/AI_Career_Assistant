"""
Application Routes

API endpoints for tracking job applications.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.job_posting import JobPosting
from app.models.user import User
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
    current_user: User = Depends(get_current_user),
) -> dict[str, int | str]:
    """
    Mark a specific job posting as applied
    for the authenticated user.
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

    try:
        application = service.mark_as_applied(
            user_id=current_user.id,
            job_posting_id=job_posting_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

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
    current_user: User = Depends(get_current_user),
) -> list[dict[str, object]]:
    """
    Retrieve applications belonging to the
    authenticated user.
    """

    service = ApplicationService(session)

    applications = service.get_all_applications(
        user_id=current_user.id,
    )

    return [
        {
            "id": application.id,
            "job_posting_id": application.job_posting_id,
            "applied_at": application.applied_at,
        }
        for application in applications
    ]