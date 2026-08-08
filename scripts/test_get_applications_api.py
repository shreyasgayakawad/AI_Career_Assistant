"""
Test Get Applications API

Integration test for retrieving all applications.
"""

# Register all SQLAlchemy models.

import app.models  # noqa: F401

from app.api.routes.applications import get_applications
from app.database.session import SessionLocal


def main() -> None:
    """
    Test retrieving all applications through the API route.
    """

    session = SessionLocal()

    try:
        print("=" * 50)
        print("Get Applications API Test")
        print("=" * 50)

        applications = get_applications(
            session=session,
        )

        print()
        print(
            f"Total Applications : "
            f"{len(applications)}"
        )

        for application in applications:
            print()
            print(
                f"Application ID : "
                f"{application['id']}"
            )
            print(
                f"Job Posting ID : "
                f"{application['job_posting_id']}"
            )
            print(
                f"Applied At     : "
                f"{application['applied_at']}"
            )

        if not applications:
            raise RuntimeError(
                "Expected at least one application."
            )

        print()
        print("Get applications API test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()