"""
Test Dashboard Candidate Profile Page

Verifies the authenticated browser profile page.
"""

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.user import User


def main() -> None:
    """
    Test the authenticated dashboard profile page.
    """

    session = SessionLocal()

    try:
        user = (
            session.query(User)
            .filter(
                User.google_subject.isnot(None),
            )
            .first()
        )

        if user is None:
            raise RuntimeError(
                "No Google-linked test user was found."
            )

        token = create_access_token(user.id)

    finally:
        session.close()

    client = TestClient(app)

    response = client.get(
        "/dashboard/profile",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    print("Status:", response.status_code)
    print(
        "Contains Candidate Profile:",
        "Candidate Profile" in response.text,
    )
    print(
        "Contains Save Profile:",
        "Save Profile" in response.text,
    )
    print(
        "Contains Phone:",
        'name="phone"' in response.text,
    )
    print(
        "Contains Skills:",
        'name="skills"' in response.text,
    )
    print(
        "Response length:",
        len(response.text),
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Dashboard profile page did not return HTTP 200."
        )

    if "Candidate Profile" not in response.text:
        raise RuntimeError(
            "Candidate Profile heading is missing."
        )

    if "Save Profile" not in response.text:
        raise RuntimeError(
            "Save Profile button is missing."
        )

    if 'name="phone"' not in response.text:
        raise RuntimeError(
            "Phone field is missing."
        )

    if 'name="skills"' not in response.text:
        raise RuntimeError(
            "Skills field is missing."
        )

    print()
    print("Dashboard profile page test passed.")


if __name__ == "__main__":
    main()