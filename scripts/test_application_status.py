"""
Test Application Status

Integration test for application status tracking (Phase 6): valid
status updates, invalid status rejection, cross-user ownership
enforcement, and confirmation that status changes do not affect the
existing exclude_applied search-exclusion behavior.
"""

import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.application import Application
from app.models.candidate_profile import CandidateProfile
from app.models.job_posting import JobPosting
from app.models.user import User
from app.services.job_search_service import JobSearchService


def _clean_up_user(session, email: str) -> None:
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

    applications = (
        session.query(Application)
        .filter(Application.user_id == user.id)
        .all()
    )

    for application in applications:
        session.delete(application)

    session.delete(user)
    session.commit()


def main() -> None:
    session = SessionLocal()

    user_a_email = "app_status_test_user_a@example.com"
    user_b_email = "app_status_test_user_b@example.com"

    try:
        _clean_up_user(session, user_a_email)
        _clean_up_user(session, user_b_email)

        user_a = User(
            name="App Status Test User A",
            email=user_a_email,
            password_hash="test_hash",
        )
        user_b = User(
            name="App Status Test User B",
            email=user_b_email,
            password_hash="test_hash",
        )
        session.add_all([user_a, user_b])
        session.commit()
        session.refresh(user_a)
        session.refresh(user_b)

        posting = session.query(JobPosting).first()

        if posting is None:
            raise RuntimeError(
                "No job postings exist. Run a job import first."
            )

        headers_a = {
            "Authorization": f"Bearer {create_access_token(user_a.id)}",
        }
        headers_b = {
            "Authorization": f"Bearer {create_access_token(user_b.id)}",
        }

        client = TestClient(app)

        print()
        print("# Application Status Test")
        print()

        # ---------------------------------------------------------
        # 1. User A applies to the posting.
        # ---------------------------------------------------------

        apply_response = client.post(
            f"/applications/{posting.id}",
            headers=headers_a,
        )

        if apply_response.status_code != 201:
            raise RuntimeError(
                "Applying to the posting failed: "
                f"{apply_response.status_code} {apply_response.text}"
            )

        application_id = apply_response.json()["id"]

        print("Application Creation                            : Passed")

        # ---------------------------------------------------------
        # 2. Default status is APPLIED.
        # ---------------------------------------------------------

        session.expire_all()
        application = session.get(Application, application_id)

        if application.status != "APPLIED":
            raise RuntimeError(
                f"Expected default status APPLIED, got "
                f"{application.status!r}"
            )

        print("Default Status Is APPLIED                       : Passed")

        # ---------------------------------------------------------
        # 3. User A updates status to INTERVIEW.
        # ---------------------------------------------------------

        update_response = client.patch(
            f"/applications/{application_id}/status",
            json={"status": "INTERVIEW"},
            headers=headers_a,
        )

        if update_response.status_code != 200:
            raise RuntimeError(
                "Valid status update failed: "
                f"{update_response.status_code} {update_response.text}"
            )

        if update_response.json()["status"] != "INTERVIEW":
            raise RuntimeError(
                "Status update response did not reflect the new "
                "status."
            )

        print("Valid Status Update                             : Passed")

        # ---------------------------------------------------------
        # 4. Status change was actually committed to the database,
        #    not just merged into the session without a commit.
        # ---------------------------------------------------------

        session.expire_all()
        persisted_application = session.get(Application, application_id)

        if persisted_application.status != "INTERVIEW":
            raise RuntimeError(
                "Status change was not persisted to the database. "
                f"Expected INTERVIEW, got "
                f"{persisted_application.status!r}"
            )

        print("Status Change Persisted To Database             : Passed")

        # ---------------------------------------------------------
        # 5. Invalid status is rejected with 400.
        # ---------------------------------------------------------

        invalid_response = client.patch(
            f"/applications/{application_id}/status",
            json={"status": "NOT_A_REAL_STATUS"},
            headers=headers_a,
        )

        if invalid_response.status_code != 400:
            raise RuntimeError(
                "Invalid status did not return 400. Got "
                f"{invalid_response.status_code}: "
                f"{invalid_response.text}"
            )

        print("Invalid Status Rejected                         : Passed")

        # ---------------------------------------------------------
        # 6. User B cannot update User A's application status.
        # ---------------------------------------------------------

        cross_user_response = client.patch(
            f"/applications/{application_id}/status",
            json={"status": "OFFER"},
            headers=headers_b,
        )

        if cross_user_response.status_code != 404:
            raise RuntimeError(
                "User B was able to update User A's application "
                f"status. Expected 404, got "
                f"{cross_user_response.status_code}."
            )

        print("Cross-User Status Update Rejected               : Passed")

        # ---------------------------------------------------------
        # 7. exclude_applied still excludes this posting from search
        #    regardless of its status -- this protects the design
        #    decision to keep Application's meaning ("has applied")
        #    unchanged by adding status tracking on top of it.
        # ---------------------------------------------------------

        search_service = JobSearchService(session)
        available_postings = search_service.search_available_postings()

        available_ids = {p.id for p in available_postings}

        if posting.id in available_ids:
            raise RuntimeError(
                "A posting with an applied application still "
                "appeared in available-jobs search after a status "
                "change -- exclude_applied regression."
            )

        print(
            "exclude_applied Still Correct (Regression Check) : Passed"
        )

        print()
        print("Application status test passed.")

    finally:
        _clean_up_user(session, user_a_email)
        _clean_up_user(session, user_b_email)
        session.close()


if __name__ == "__main__":
    main()