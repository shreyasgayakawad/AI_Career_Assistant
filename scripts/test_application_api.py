"""
Application API Test

Tests authenticated application endpoints and
user-specific application isolation.
"""

import app.models  # noqa: F401

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.routes.applications import (
    get_applications,
    mark_job_as_applied,
)
from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.models.user import User


def main() -> None:
    """
    Test authenticated application API behavior.
    """

    session = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Find a valid job posting.
        # ---------------------------------------------------------

        posting = (
            session.query(JobPosting)
            .order_by(JobPosting.id)
            .first()
        )

        if posting is None:
            raise RuntimeError(
                "No job postings found in the database."
            )

        # ---------------------------------------------------------
        # Create two test users.
        # ---------------------------------------------------------

        user_a_email = (
            "application_api_user_a@example.com"
        )

        user_b_email = (
            "application_api_user_b@example.com"
        )

        for email in (
            user_a_email,
            user_b_email,
        ):
            existing_user = (
                session.query(User)
                .filter(User.email == email)
                .first()
            )

            if existing_user:
                session.delete(existing_user)

        session.commit()

        user_a = User(
            name="Application API User A",
            email=user_a_email,
            password_hash="test_hash",
        )

        user_b = User(
            name="Application API User B",
            email=user_b_email,
            password_hash="test_hash",
        )

        session.add_all(
            [
                user_a,
                user_b,
            ]
        )

        session.commit()

        session.refresh(user_a)
        session.refresh(user_b)

        # ---------------------------------------------------------
        # Create JWT credentials.
        # ---------------------------------------------------------

        token_a = create_access_token(
            user_id=user_a.id,
        )

        token_b = create_access_token(
            user_id=user_b.id,
        )

        credentials_a = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_a,
        )

        credentials_b = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_b,
        )

        print()
        print("# Application API Test")
        print()

        print(f"Job Posting ID : {posting.id}")
        print(f"Job Title      : {posting.title}")

        # ---------------------------------------------------------
        # Clean up previous application for User A.
        # ---------------------------------------------------------

        existing_application = (
            session.query(Application)
            .filter(
                Application.user_id == user_a.id,
                Application.job_posting_id == posting.id,
            )
            .first()
        )

        if existing_application:
            session.delete(existing_application)
            session.commit()

        # ---------------------------------------------------------
        # 1. User A applies.
        # ---------------------------------------------------------

        response = mark_job_as_applied(
            job_posting_id=posting.id,
            session=session,
            current_user=user_a,
        )

        print()
        print(f"Application ID : {response['id']}")
        print(
            f"Job Posting ID : "
            f"{response['job_posting_id']}"
        )
        print(f"Message        : {response['message']}")

        if response["job_posting_id"] != posting.id:
            raise RuntimeError(
                "Job posting ID does not match."
            )

        print()
        print("Application Creation : Passed")

        # ---------------------------------------------------------
        # 2. Duplicate application for User A.
        # ---------------------------------------------------------

        try:
            mark_job_as_applied(
                job_posting_id=posting.id,
                session=session,
                current_user=user_a,
            )

            raise RuntimeError(
                "Duplicate application was created."
            )

        except HTTPException as exc:
            if exc.status_code != 409:
                raise RuntimeError(
                    "Expected HTTP 409 for duplicate "
                    f"application, got {exc.status_code}."
                )

        print(
            "Duplicate Prevention   : Passed"
        )

        # ---------------------------------------------------------
        # 3. User B can apply to the same posting.
        # ---------------------------------------------------------

        user_b_application = mark_job_as_applied(
            job_posting_id=posting.id,
            session=session,
            current_user=user_b,
        )

        if user_b_application["id"] == response["id"]:
            raise RuntimeError(
                "User B incorrectly received User A's "
                "application."
            )

        print(
            "Multi-User Application : Passed"
        )

        # ---------------------------------------------------------
        # 4. User A sees only User A's application.
        # ---------------------------------------------------------

        user_a_applications = get_applications(
            session=session,
            current_user=user_a,
        )

        if len(user_a_applications) != 1:
            raise RuntimeError(
                "User A should have exactly one application."
            )

        if (
            user_a_applications[0]["id"]
            != response["id"]
        ):
            raise RuntimeError(
                "User A received another user's application."
            )

        print(
            "User Application Isolation : Passed"
        )

        # ---------------------------------------------------------
        # 5. User B sees only User B's application.
        # ---------------------------------------------------------

        user_b_applications = get_applications(
            session=session,
            current_user=user_b,
        )

        if len(user_b_applications) != 1:
            raise RuntimeError(
                "User B should have exactly one application."
            )

        if (
            user_b_applications[0]["id"]
            != user_b_application["id"]
        ):
            raise RuntimeError(
                "User B received another user's application."
            )

        print(
            "Second User Isolation       : Passed"
        )

        # ---------------------------------------------------------
        # 6. Invalid posting.
        # ---------------------------------------------------------

        invalid_posting_id = 999999999

        try:
            mark_job_as_applied(
                job_posting_id=invalid_posting_id,
                session=session,
                current_user=user_a,
            )

            raise RuntimeError(
                "Invalid job posting was accepted."
            )

        except HTTPException as exc:
            if exc.status_code != 404:
                raise RuntimeError(
                    "Expected HTTP 404 for invalid "
                    f"posting, got {exc.status_code}."
                )

        print(
            "Invalid Posting        : 404 Passed"
        )

        print()
        print(
            "Application API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()