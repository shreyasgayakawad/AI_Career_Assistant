"""
Google OAuth Token Client

Exchanges Google authorization codes and verifies Google ID tokens.
"""

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import id_token

from app.config.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleTokenClient:
    """
    Client for Google OpenID Connect token operations.
    """

    def exchange_code(self, code: str) -> dict:
        """
        Exchange a Google authorization code for tokens.
        """

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
        }

        try:
            response = httpx.post(
                GOOGLE_TOKEN_URL,
                data=payload,
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            raise ValueError(
                "Unable to connect to Google token endpoint."
            ) from exc

        if response.status_code != 200:
            raise ValueError("Google token exchange failed.")

        try:
            token_data = response.json()
        except ValueError as exc:
            raise ValueError(
                "Google token response was invalid."
            ) from exc

        if not token_data.get("id_token"):
            raise ValueError(
                "Google token response did not contain an ID token."
            )

        return token_data

    def verify_identity(self, encoded_id_token: str) -> dict:
        """
        Verify a Google ID token and return required identity claims.
        """

        try:
            claims = id_token.verify_oauth2_token(
                encoded_id_token,
                Request(),
                GOOGLE_CLIENT_ID,
            )
        except ValueError as exc:
            raise ValueError("Google ID token was invalid.") from exc

        subject = claims.get("sub")
        email = claims.get("email")
        email_verified = claims.get("email_verified")

        if not isinstance(subject, str) or not subject:
            raise ValueError(
                "Google ID token did not contain a subject."
            )

        if not isinstance(email, str) or not email:
            raise ValueError(
                "Google ID token did not contain an email."
            )

        if email_verified is not True:
            raise ValueError("Google email must be verified.")

        return {
            "sub": subject,
            "email": email,
            "email_verified": email_verified,
        }
