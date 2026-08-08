"""
Portal Connection Routes

API endpoints for managing authenticated user's
connections to external job platforms.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.portal_connection_service import (
    PortalConnectionService,
)


router = APIRouter(
    prefix="/portal-connections",
    tags=["Portal Connections"],
)


class CreatePortalConnectionRequest(BaseModel):
    """
    Request body for creating a portal connection.
    """

    platform: str
    login_email: str
    credential_reference: str | None = None


class PortalConnectionResponse(BaseModel):
    """
    Response representing a portal connection.
    """

    id: int
    platform: str
    login_email: str
    enabled: bool
    status: str


@router.post(
    "/",
    response_model=PortalConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portal_connection(
    request: CreatePortalConnectionRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortalConnectionResponse:
    """
    Create a portal connection for the authenticated user.
    """

    service = PortalConnectionService(session)

    try:
        connection = service.create_connection(
            user_id=current_user.id,
            platform=request.platform,
            login_email=request.login_email,
            credential_reference=request.credential_reference,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return PortalConnectionResponse(
        id=connection.id,
        platform=connection.platform,
        login_email=connection.login_email,
        enabled=connection.enabled,
        status=connection.status,
    )


@router.get(
    "/",
    response_model=list[PortalConnectionResponse],
)
def get_portal_connections(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PortalConnectionResponse]:
    """
    Retrieve portal connections belonging to
    the authenticated user.
    """

    service = PortalConnectionService(session)

    connections = service.get_all_connections(
        user_id=current_user.id,
    )

    return [
        PortalConnectionResponse(
            id=connection.id,
            platform=connection.platform,
            login_email=connection.login_email,
            enabled=connection.enabled,
            status=connection.status,
        )
        for connection in connections
    ]