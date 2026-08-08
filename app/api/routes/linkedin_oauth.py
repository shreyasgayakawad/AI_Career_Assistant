"""
LinkedIn OAuth Routes

Provides authorization and callback endpoints for LinkedIn
OpenID Connect authentication.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.config.settings import LINKEDIN_ENABLED, LINKEDIN_SCOPES
from app.connectors.linkedin_oauth import build_authorization_url
from app.connectors.linkedin_token_client import (
    LinkedInTokenClient,
)
from app.models.user import User
from app.services.oauth_state_service import OAuthStateService
from app.services.portal_connection_service import (
    PortalConnectionService,
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

    state_service = OAuthStateService(
        session,
    )

    oauth_state = state_service.create_state(
        user_id=current_user.id,
        platform="LinkedIn",
    )

    authorization_url = build_authorization_url(
        state=oauth_state.state,
    )

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
    Handle the LinkedIn OAuth callback and create a portal connection.
    """

    if not LINKEDIN_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn integration is disabled.",
        )

    if error:
        detail = "LinkedIn authorization failed."

        if error_description:
            detail = f"{detail} {error_description}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LinkedIn authorization code is missing.",
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state is missing.",
        )

    state_service = OAuthStateService(
        session,
    )

    oauth_state = state_service.get_state(
        state=state,
    )

    if oauth_state is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state.",
        )

    try:
        state_service.validate_state(
            state=state,
            user_id=oauth_state.user_id,
            platform="LinkedIn",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    token_client = LinkedInTokenClient()

    try:
        token_data = token_client.exchange_code(
            code=code,
        )

        access_token = token_data.get(
            "access_token",
        )

        if not access_token:
            raise ValueError(
                "LinkedIn token response did not contain an access token."
            )

        userinfo = token_client.get_userinfo(
            access_token=access_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    expires_in = token_data.get(
        "expires_in",
    )

    token_expires_at = None

    if expires_in is not None:
        try:
            token_expires_at = (
                datetime.now(timezone.utc)
                + timedelta(
                    seconds=int(expires_in),
                )
            ).replace(
                tzinfo=None,
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LinkedIn token expiration was invalid.",
            ) from exc

    scopes = token_data.get(
        "scope",
    ) or LINKEDIN_SCOPES

    portal_connection_service = PortalConnectionService(
        session,
    )

    try:
        connection = (
            portal_connection_service.create_oauth_connection(
                user_id=oauth_state.user_id,
                platform="LinkedIn",
                login_email=userinfo.get("email", ""),
                external_user_id=str(
                    userinfo["sub"],
                ),
                oauth_scopes=str(scopes),
                access_token=access_token,
                token_expires_at=token_expires_at,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
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