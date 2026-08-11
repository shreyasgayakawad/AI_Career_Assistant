"""
Application Settings

Loads configuration from environment variables.
"""

import os

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# JWT Authentication
# ---------------------------------------------------------------------------

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
)

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured."
    )


# ---------------------------------------------------------------------------
# LinkedIn OAuth
# ---------------------------------------------------------------------------

LINKEDIN_ENABLED = os.getenv(
    "LINKEDIN_ENABLED",
    "false",
).lower() == "true"

LINKEDIN_CLIENT_ID = os.getenv(
    "LINKEDIN_CLIENT_ID",
)

LINKEDIN_CLIENT_SECRET = os.getenv(
    "LINKEDIN_CLIENT_SECRET",
)

LINKEDIN_REDIRECT_URI = os.getenv(
    "LINKEDIN_REDIRECT_URI",
    "http://localhost:8000/auth/linkedin/callback",
)

LINKEDIN_SCOPES = os.getenv(
    "LINKEDIN_SCOPES",
    "openid profile email",
)


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

GOOGLE_ENABLED = os.getenv(
    "GOOGLE_ENABLED",
    "false",
).lower() == "true"

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
)

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/auth/google/callback",
)

GOOGLE_SCOPES = os.getenv(
    "GOOGLE_SCOPES",
    "openid email profile",
)

GOOGLE_LOGIN_SUCCESS_REDIRECT_URI = os.getenv(
    "GOOGLE_LOGIN_SUCCESS_REDIRECT_URI",
    "/session",
)


# ---------------------------------------------------------------------------
# Browser Session Cookie
# ---------------------------------------------------------------------------

AUTH_COOKIE_NAME = os.getenv(
    "AUTH_COOKIE_NAME",
    "career_access_token",
)

AUTH_COOKIE_SECURE = os.getenv(
    "AUTH_COOKIE_SECURE",
    "false",
).lower() == "true"


# ---------------------------------------------------------------------------
# Credential Encryption
# ---------------------------------------------------------------------------

CREDENTIAL_ENCRYPTION_KEY = os.getenv(
    "CREDENTIAL_ENCRYPTION_KEY",
)

if not CREDENTIAL_ENCRYPTION_KEY:
    raise RuntimeError(
        "CREDENTIAL_ENCRYPTION_KEY is not configured."
    )