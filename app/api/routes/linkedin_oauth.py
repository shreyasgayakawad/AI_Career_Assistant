"""
LinkedIn OAuth Routes

Provides authorization and callback endpoints for LinkedIn
OpenID Connect authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.config.settings import LINKEDIN_ENABLED
from app.models.user import User
from app.services.linkedin.oauth_service import (
    LinkedInOAuthService,
)

router = APIRouter(
    prefix="/auth/linkedin",
    tags=["LinkedIn OAuth"],
)


@router.get(
    "/authorize",
)
def authorize_linkedin(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Start the LinkedIn OAuth authorization flow.
    """

    if not LINKEDIN_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn integration is disabled.",
        )

    service = LinkedInOAuthService(
        session,
    )

    try:
        authorization_url = (
            service.create_authorization_url(
                user_id=current_user.id,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return RedirectResponse(
        url=authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.get(
    "/callback",
)
def linkedin_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    session: Session = Depends(get_db),
) -> dict[str, str | int | None]:
    """
    Handle the LinkedIn OAuth callback and create or update
    a portal connection.
    """

    if not LINKEDIN_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn integration is disabled.",
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state is missing.",
        )

    service = LinkedInOAuthService(
        session,
    )

    try:
        connection, userinfo = service.handle_callback(
            state=state,
            code=code,
            error=error,
            error_description=error_description,
        )

    except ValueError as exc:
        detail = str(exc)

        if detail in {
            "Invalid OAuth state.",
            "OAuth state does not belong to the user.",
            "OAuth state platform mismatch.",
            "OAuth state has expired.",
            "LinkedIn authorization code is missing.",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            ) from exc

        if detail.startswith(
            "LinkedIn authorization failed."
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from exc

    return {
        "message": "LinkedIn OAuth connection created.",
        "connection_id": connection.id,
        "linkedin_user_id": connection.external_user_id,
        "name": userinfo.get("name"),
        "email": userinfo.get("email"),
        "token_expires_at": (
            connection.token_expires_at.isoformat()
            if connection.token_expires_at
            else None
        ),
    }