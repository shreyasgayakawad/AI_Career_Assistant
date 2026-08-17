"""
Test Candidate Profile Structured Entries

Integration test for the Phase 4 structured candidate profile
endpoints: skills, work experience, and education entries.

Covers add/list/remove for each entity type, case-insensitive
duplicate-skill deduplication, lazy profile creation on first write
(no prior GET required), invalid-date rejection, and cross-user
ownership enforcement on delete.
"""

import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.user import User


def _clean_up_user(session, email: str) -> None:
    """
    Remove a test user and their candidate profile (which cascades
    to skills/work experience/education entries) if they exist.
    """

    user = session.query(User).filter(User.email == email).first()

    if user is None:
        return

    profile = (
        session.query(CandidateProfile)
        .filter(CandidateProfile.user_id == user.id)
        .first()
    )

    if profile is not None:
        session.delete(profile)

    session.delete(user)
    session.commit()


def main() -> None:
    """
    Test structured candidate profile endpoints end-to-end.
    """

    session = SessionLocal()

    user_a_email = "phase4_test_user_a@example.com"
    user_b_email = "phase4_test_user_b@example.com"

    try:
        _clean_up_user(session, user_a_email)
        _clean_up_user(session, user_b_email)

        user_a = User(
            name="Phase 4 Test User A",
            email=user_a_email,
            password_hash="test_hash",
        )
        user_b = User(
            name="Phase 4 Test User B",
            email=user_b_email,
            password_hash="test_hash",
        )

        session.add_all([user_a, user_b])
        session.commit()
        session.refresh(user_a)
        session.refresh(user_b)

        headers_a = {
            "Authorization": f"Bearer {create_access_token(user_a.id)}",
        }
        headers_b = {
            "Authorization": f"Bearer {create_access_token(user_b.id)}",
        }

        client = TestClient(app)

        print()
        print("# Candidate Profile Structured Entries Test")
        print()

        # ---------------------------------------------------------
        # 1. Add a skill without ever calling GET /profile/ first.
        #    Confirms the profile is lazily created on first write.
        # ---------------------------------------------------------

        response = client.post(
            "/profile/skills",
            json={"name": "Python"},
            headers=headers_a,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Adding a skill without a prior GET failed: "
                f"{response.status_code} {response.text}"
            )

        skill_id = response.json()["id"]

        if response.json()["name"] != "Python":
            raise RuntimeError(
                "Created skill has the wrong name."
            )

        print("Lazy Profile Creation on First Write : Passed")

        # ---------------------------------------------------------
        # 2. Duplicate skill name should return the existing entry.
        # ---------------------------------------------------------

        duplicate_response = client.post(
            "/profile/skills",
            json={"name": "python"},
            headers=headers_a,
        )

        if duplicate_response.status_code != 200:
            raise RuntimeError(
                "Duplicate skill request failed: "
                f"{duplicate_response.status_code} "
                f"{duplicate_response.text}"
            )

        if duplicate_response.json()["id"] != skill_id:
            raise RuntimeError(
                "Duplicate skill (case-insensitive) created a "
                "second row instead of returning the existing one."
            )

        print("Duplicate Skill Deduplication         : Passed")

        # ---------------------------------------------------------
        # 3. GET /profile/ shows the skill in skills_list.
        # ---------------------------------------------------------

        profile_response = client.get("/profile/", headers=headers_a)

        if profile_response.status_code != 200:
            raise RuntimeError(
                "GET /profile/ failed: "
                f"{profile_response.status_code} "
                f"{profile_response.text}"
            )

        skill_ids_in_profile = {
            skill["id"]
            for skill in profile_response.json()["skills_list"]
        }

        if skill_id not in skill_ids_in_profile:
            raise RuntimeError(
                "Added skill did not appear in GET /profile/ "
                "skills_list."
            )

        print("Skill Visible in GET /profile/        : Passed")

        # ---------------------------------------------------------
        # 4. User B cannot delete User A's skill.
        # ---------------------------------------------------------

        cross_user_delete = client.delete(
            f"/profile/skills/{skill_id}",
            headers=headers_b,
        )

        if cross_user_delete.status_code != 404:
            raise RuntimeError(
                "User B was able to delete User A's skill. "
                f"Expected 404, got {cross_user_delete.status_code}."
            )

        print("Cross-User Skill Deletion Rejected    : Passed")

        # ---------------------------------------------------------
        # 5. User A can delete their own skill.
        # ---------------------------------------------------------

        own_delete = client.delete(
            f"/profile/skills/{skill_id}",
            headers=headers_a,
        )

        if own_delete.status_code != 200:
            raise RuntimeError(
                "User A could not delete their own skill: "
                f"{own_delete.status_code} {own_delete.text}"
            )

        if own_delete.json()["id"] != skill_id:
            raise RuntimeError(
                "Delete response did not match the deleted skill."
            )

        print("Own Skill Deletion                    : Passed")

        # ---------------------------------------------------------
        # 6. Deleted skill no longer appears in GET /profile/.
        # ---------------------------------------------------------

        after_delete = client.get("/profile/", headers=headers_a)

        remaining_skill_ids = {
            skill["id"]
            for skill in after_delete.json()["skills_list"]
        }

        if skill_id in remaining_skill_ids:
            raise RuntimeError(
                "Deleted skill still appears in GET /profile/."
            )

        print("Skill Removed From GET /profile/      : Passed")

        # ---------------------------------------------------------
        # 7. Work experience: add, cross-user rejected, own delete.
        # ---------------------------------------------------------

        we_response = client.post(
            "/profile/work-experience",
            json={
                "company_name": "Acme Corp",
                "job_title": "Engineer",
                "start_date": "2020-01-01",
                "end_date": "2022-12-31",
                "description": "Built things.",
            },
            headers=headers_a,
        )

        if we_response.status_code != 200:
            raise RuntimeError(
                "Adding work experience failed: "
                f"{we_response.status_code} {we_response.text}"
            )

        experience_id = we_response.json()["id"]

        print("Work Experience Creation              : Passed")

        we_cross_delete = client.delete(
            f"/profile/work-experience/{experience_id}",
            headers=headers_b,
        )

        if we_cross_delete.status_code != 404:
            raise RuntimeError(
                "User B was able to delete User A's work "
                f"experience. Expected 404, got "
                f"{we_cross_delete.status_code}."
            )

        print("Cross-User Work Experience Rejected   : Passed")

        we_delete = client.delete(
            f"/profile/work-experience/{experience_id}",
            headers=headers_a,
        )

        if we_delete.status_code != 200:
            raise RuntimeError(
                "User A could not delete their own work "
                f"experience: {we_delete.status_code} "
                f"{we_delete.text}"
            )

        print("Own Work Experience Deletion          : Passed")

        # ---------------------------------------------------------
        # 8. Work experience: invalid date returns 400, not 500.
        # ---------------------------------------------------------

        bad_date_response = client.post(
            "/profile/work-experience",
            json={
                "company_name": "Bad Dates Inc",
                "job_title": "Tester",
                "start_date": "not-a-date",
                "end_date": None,
                "description": None,
            },
            headers=headers_a,
        )

        if bad_date_response.status_code != 400:
            raise RuntimeError(
                "Invalid start_date did not return 400. Got "
                f"{bad_date_response.status_code}: "
                f"{bad_date_response.text}"
            )

        print("Invalid Work Experience Date Rejected : Passed")

        # ---------------------------------------------------------
        # 9. Education: add, cross-user rejected, own delete works.
        # ---------------------------------------------------------

        edu_response = client.post(
            "/profile/education",
            json={
                "institution": "State University",
                "degree": "BS",
                "field_of_study": "Computer Science",
                "start_date": "2016-09-01",
                "end_date": "2020-05-31",
            },
            headers=headers_a,
        )

        if edu_response.status_code != 200:
            raise RuntimeError(
                "Adding education failed: "
                f"{edu_response.status_code} {edu_response.text}"
            )

        education_id = edu_response.json()["id"]

        print("Education Creation                    : Passed")

        edu_cross_delete = client.delete(
            f"/profile/education/{education_id}",
            headers=headers_b,
        )

        if edu_cross_delete.status_code != 404:
            raise RuntimeError(
                "User B was able to delete User A's education "
                f"entry. Expected 404, got "
                f"{edu_cross_delete.status_code}."
            )

        print("Cross-User Education Rejected         : Passed")

        edu_delete = client.delete(
            f"/profile/education/{education_id}",
            headers=headers_a,
        )

        if edu_delete.status_code != 200:
            raise RuntimeError(
                "User A could not delete their own education "
                f"entry: {edu_delete.status_code} {edu_delete.text}"
            )

        print("Own Education Deletion                : Passed")

        # ---------------------------------------------------------
        # 10. Education: invalid date returns 400, not 500.
        # ---------------------------------------------------------

        bad_edu_date_response = client.post(
            "/profile/education",
            json={
                "institution": "Bad Dates University",
                "degree": "BS",
                "field_of_study": None,
                "start_date": "also-not-a-date",
                "end_date": None,
            },
            headers=headers_a,
        )

        if bad_edu_date_response.status_code != 400:
            raise RuntimeError(
                "Invalid education start_date did not return "
                f"400. Got {bad_edu_date_response.status_code}: "
                f"{bad_edu_date_response.text}"
            )

        print("Invalid Education Date Rejected       : Passed")

        # ---------------------------------------------------------
        # 11. Old free-text fields remain untouched throughout.
        # ---------------------------------------------------------

        final_profile = client.get(
            "/profile/",
            headers=headers_a,
        ).json()

        if final_profile["skills"] is not None:
            raise RuntimeError(
                "Free-text 'skills' field was unexpectedly "
                "modified by structured entry operations."
            )

        print("Free-Text Fields Untouched            : Passed")

        print()
        print("Candidate profile structured entries test passed.")

    finally:
        _clean_up_user(session, user_a_email)
        _clean_up_user(session, user_b_email)
        session.close()


if __name__ == "__main__":
    main()