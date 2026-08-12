"""
Test Candidate Profile API

Verifies authenticated profile creation, retrieval, and updates.
"""

import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.user import User


def main() -> None:
    """
    Test the candidate profile API.
    """

    session = SessionLocal()
    user = None
    profile = None

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

        client = TestClient(app)

        print("=" * 50)
        print("Candidate Profile API Test")
        print("=" * 50)

        unauthenticated_response = client.get(
            "/profile/",
        )

        if unauthenticated_response.status_code != 401:
            raise RuntimeError(
                "Unauthenticated profile access was not rejected."
            )

        print("Unauthenticated Access    : Passed")

        response = client.get(
            "/profile/",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Authenticated profile retrieval failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        profile_data = response.json()

        if profile_data["user_id"] != user.id:
            raise RuntimeError(
                "Profile belongs to the wrong user."
            )

        print("Authenticated Retrieval    : Passed")

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

        update_response = client.put(
            "/profile/",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        if update_response.status_code != 200:
            raise RuntimeError(
                "Profile update failed: "
                f"{update_response.status_code} "
                f"{update_response.text}"
            )

        updated_data = update_response.json()

        for field, expected_value in payload.items():
            if updated_data[field] != expected_value:
                raise RuntimeError(
                    f"Profile field '{field}' was not updated."
                )

        if updated_data["user_id"] != user.id:
            raise RuntimeError(
                "Updated profile belongs to the wrong user."
            )

        print("Profile Update             : Passed")

        session.expire_all()

        profile = (
            session.query(CandidateProfile)
            .filter(
                CandidateProfile.user_id == user.id,
            )
            .first()
        )

        if profile is None:
            raise RuntimeError(
                "Updated candidate profile was not persisted."
            )

        if profile.skills != payload["skills"]:
            raise RuntimeError(
                "Updated profile was not persisted correctly."
            )

        print("Database Persistence       : Passed")

        second_response = client.get(
            "/profile/",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        if second_response.status_code != 200:
            raise RuntimeError(
                "Profile retrieval after update failed."
            )

        second_data = second_response.json()

        if second_data["skills"] != payload["skills"]:
            raise RuntimeError(
                "Profile update was not retained."
            )

        print("Updated Profile Retrieval  : Passed")

        print()
        print("Candidate profile API test passed.")

    finally:
        if user is not None:
            profile = (
                session.query(CandidateProfile)
                .filter(
                    CandidateProfile.user_id == user.id,
                )
                .first()
            )

            if profile is not None:
                session.delete(profile)
                session.commit()

        session.close()


if __name__ == "__main__":
    main()