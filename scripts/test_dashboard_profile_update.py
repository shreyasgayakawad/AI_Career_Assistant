"""
Test Dashboard Candidate Profile Update

Verifies that the authenticated browser profile form
updates the candidate profile and redirects correctly.
"""

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.user import User


def main() -> None:
    """
    Test the authenticated dashboard profile update.
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

    payload = {
        "phone": "9876543210",
        "location": "Pune, India",
        "professional_summary": (
            "Software engineer building "
            "AI-powered career tools."
        ),
        "skills": (
            "Python, FastAPI, SQLAlchemy, PostgreSQL"
        ),
        "experience": (
            "AI Career Assistant Developer"
        ),
        "education": "Bachelor of Engineering",
    }

    response = client.post(
        "/dashboard/profile",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
        },
        follow_redirects=False,
    )

    print("Status:", response.status_code)
    print(
        "Location:",
        response.headers.get("location"),
    )

    if response.status_code != 303:
        raise RuntimeError(
            "Profile update did not return HTTP 303."
        )

    if response.headers.get("location") != "/dashboard/profile":
        raise RuntimeError(
            "Profile update redirected to the wrong location."
        )

    print("Browser Profile Update     : Passed")
    print("Correct Redirect            : Passed")

    session = SessionLocal()

    try:
        profile = (
            session.query(CandidateProfile)
            .filter(
                CandidateProfile.user_id == user.id,
            )
            .first()
        )

        if profile is None:
            raise RuntimeError(
                "Candidate profile was not found."
            )

        if profile.phone != payload["phone"]:
            raise RuntimeError(
                "Phone was not persisted correctly."
            )

        if profile.location != payload["location"]:
            raise RuntimeError(
                "Location was not persisted correctly."
            )

        if (
            profile.professional_summary
            != payload["professional_summary"]
        ):
            raise RuntimeError(
                "Professional summary was not persisted "
                "correctly."
            )

        if profile.skills != payload["skills"]:
            raise RuntimeError(
                "Skills were not persisted correctly."
            )

        if profile.experience != payload["experience"]:
            raise RuntimeError(
                "Experience was not persisted correctly."
            )

        if profile.education != payload["education"]:
            raise RuntimeError(
                "Education was not persisted correctly."
            )

        print("Database Persistence       : Passed")

    finally:
        session.close()

    response = client.get(
        "/dashboard/profile",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Profile page could not be retrieved after update."
        )

    if payload["phone"] not in response.text:
        raise RuntimeError(
            "Saved phone was not displayed."
        )

    if payload["location"] not in response.text:
        raise RuntimeError(
            "Saved location was not displayed."
        )

    if payload["skills"] not in response.text:
        raise RuntimeError(
            "Saved skills were not displayed."
        )

    print("Updated Profile Display    : Passed")

    print()
    print("Dashboard profile update test passed.")


if __name__ == "__main__":
    main()