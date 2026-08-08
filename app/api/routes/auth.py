"""
Authentication Routes

API endpoints for user registration and authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.jwt import create_access_token
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    """
    Request body for user registration.
    """

    name: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    """
    Response returned after successful registration.
    """

    id: int
    name: str
    email: str


class LoginRequest(BaseModel):
    """
    Request body for user login.
    """

    email: str
    password: str


class LoginResponse(BaseModel):
    """
    Response returned after successful login.
    """

    access_token: str
    token_type: str
    id: int
    name: str
    email: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user account.
    """

    service = AuthService(session)

    try:
        user = service.register_user(
            name=request.name,
            email=request.email,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RegisterResponse(
        id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    session: Session = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate a user and return an access token.
    """

    service = AuthService(session)

    try:
        user = service.login_user(
            email=request.email,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token = create_access_token(
        user_id=user.id,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        id=user.id,
        name=user.name,
        email=user.email,
    )