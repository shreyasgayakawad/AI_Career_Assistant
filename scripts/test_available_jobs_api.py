"""
Test Available Jobs API

Integration test for the job listing API.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.jobs import get_jobs
from app.database.session import SessionLocal
from app.models.application import Application


def main() -> None:
    """
    Test the available jobs API.
    """

    session = SessionLocal()

    try:
        print("=" * 60)
        print("Available Jobs API Test")
        print("=" * 60)

        # -----------------------------------------------------------
        # Test 1: Unfiltered available jobs.
        # -----------------------------------------------------------

        jobs = get_jobs(
            session=session,
        )

        print()
        print(
            f"Available Job Postings : {len(jobs)}"
        )

        for job in jobs[:10]:
            print()
            print(
                f"Posting ID : {job.id}"
            )
            print(
                f"Job ID     : {job.job_id}"
            )
            print(
                f"Title      : {job.title}"
            )
            print(
                f"Company    : {job.company}"
            )
            print(
                f"Location   : {job.location}"
            )
            print(
                f"Work Mode  : {job.work_mode}"
            )
            print(
                f"URL        : {job.posting_url}"
            )

        # -----------------------------------------------------------
        # Test 2: Applied postings are excluded.
        # -----------------------------------------------------------

        for job in jobs:
            application = (
                session.query(Application)
                .filter(
                    Application.job_posting_id
                    == job.id,
                )
                .first()
            )

            if application is not None:
                raise RuntimeError(
                    "An applied job posting was returned "
                    f"by the API: {job.id}"
                )

        print()
        print(
            "Applied Posting Exclusion : Passed"
        )

        # -----------------------------------------------------------
        # Test 3: Posting identity and work mode.
        # -----------------------------------------------------------

        for job in jobs:
            if job.id is None:
                raise RuntimeError(
                    "Posting ID is missing."
                )

            if job.job_id is None:
                raise RuntimeError(
                    "Logical Job ID is missing."
                )

            if not job.work_mode:
                raise RuntimeError(
                    "Work mode is missing."
                )

        print(
            "Posting Identity          : Passed"
        )
        print(
            "Work Mode Presence        : Passed"
        )

        # -----------------------------------------------------------
        # Test 4: Exact work-mode filtering.
        # -----------------------------------------------------------

        for work_mode in (
            "REMOTE",
            "HYBRID",
            "ONSITE",
            "UNKNOWN",
        ):
            filtered_jobs = get_jobs(
                work_mode=work_mode,
                session=session,
            )

            for job in filtered_jobs:
                if job.work_mode != work_mode:
                    raise RuntimeError(
                        "API work mode filter returned "
                        f"'{job.work_mode}' for "
                        f"requested '{work_mode}'."
                    )

            print(
                f"{work_mode} Filter          : Passed"
            )

        # -----------------------------------------------------------
        # Test 5: Invalid work mode.
        # -----------------------------------------------------------

        try:
            get_jobs(
                work_mode="INVALID",
                session=session,
            )

        except HTTPException as exc:
            if exc.status_code != 400:
                raise RuntimeError(
                    "Expected status code 400, "
                    f"got {exc.status_code}."
                ) from exc

        else:
            raise RuntimeError(
                "Expected HTTPException for "
                "invalid work mode."
            )

        print(
            "Invalid Work Mode         : Passed"
        )

        print()
        print(
            "Available jobs API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()