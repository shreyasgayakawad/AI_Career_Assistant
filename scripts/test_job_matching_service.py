"""
Test Job Matching Service

Integration test for JobMatchingService: deterministic skill-overlap
scoring against synthetic postings (for exact, reproducible
assertions) plus real database data (for a realistic smoke test).

Also tests the GET /jobs/{job_posting_id}/match-score API endpoint
directly through a real authenticated request -- this is the layer
that previously had a bug where the candidate profile lookup used
the wrong key entirely, crashing for every real user. A purely
service-level test could never have caught that class of bug.
"""

import app.models  # noqa: F401

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.models.user import User
from app.services.job_matching_service import JobMatchingService


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

    session.delete(user)
    session.commit()


def _create_user_with_skills(
    session,
    email: str,
    name: str,
    skills: list[str],
) -> tuple[User, CandidateProfile]:
    user = User(
        name=name,
        email=email,
        password_hash="test_hash",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    profile = CandidateProfile(user_id=user.id)
    session.add(profile)
    session.commit()
    session.refresh(profile)

    for skill_name in skills:
        session.add(
            CandidateSkill(
                candidate_profile_id=profile.id,
                name=skill_name,
            )
        )

    session.commit()
    session.refresh(profile)

    return user, profile


def main() -> None:
    session = SessionLocal()

    user_a_email = "matching_test_user_a@example.com"
    user_b_email = "matching_test_user_b@example.com"
    user_c_email = "matching_test_user_c@example.com"
    new_user_email = "matching_test_brand_new@example.com"

    try:
        for email in (
            user_a_email,
            user_b_email,
            user_c_email,
            new_user_email,
        ):
            _clean_up_user(session, email)

        user_a, profile_a = _create_user_with_skills(
            session,
            user_a_email,
            "Matching Test User A",
            ["Python", "Docker"],
        )
        user_b, profile_b = _create_user_with_skills(
            session,
            user_b_email,
            "Matching Test User B",
            ["Java"],
        )
        user_c, profile_c = _create_user_with_skills(
            session,
            user_c_email,
            "Matching Test User C",
            [],
        )

        matching_service = JobMatchingService()

        print()
        print("# Job Matching Service Test")
        print()

        # ---------------------------------------------------------
        # 1. Word-boundary regression, against an in-memory
        #    (unpersisted) posting so the result is exact and
        #    reproducible regardless of what's actually in the
        #    database.
        # ---------------------------------------------------------

        javascript_posting = JobPosting(
            title="Senior JavaScript Developer",
            description="We need someone who loves JavaScript.",
            location=None,
            work_mode="UNKNOWN",
            posting_url="https://example.com/js-job",
        )

        result_java = matching_service.calculate_match_score(
            candidate_profile=profile_b,
            job_posting=javascript_posting,
        )

        if "Java" in result_java.matched_skills:
            raise RuntimeError(
                "'Java' incorrectly matched inside 'JavaScript' -- "
                "word-boundary regex regression."
            )

        if result_java.overall_score != 0.0:
            raise RuntimeError(
                "Expected 0% for 'Java' against a JavaScript-only "
                f"posting, got {result_java.overall_score}%"
            )

        print("Word-Boundary Regression (Java vs JavaScript) : Passed")

        python_posting = JobPosting(
            title="Python Developer",
            description="Docker experience is a plus.",
            location=None,
            work_mode="UNKNOWN",
            posting_url="https://example.com/py-job",
        )

        result_python = matching_service.calculate_match_score(
            candidate_profile=profile_a,
            job_posting=python_posting,
        )

        if result_python.overall_score != 100.0:
            raise RuntimeError(
                "Expected 100% match, got "
                f"{result_python.overall_score}%"
            )

        if set(result_python.matched_skills) != {"Python", "Docker"}:
            raise RuntimeError(
                "Expected both Python and Docker to match, got "
                f"{result_python.matched_skills}"
            )

        print("Full Skill Match (Python + Docker)             : Passed")

        # ---------------------------------------------------------
        # 2. Zero-skills case returns None, not 0.0.
        # ---------------------------------------------------------

        result_zero = matching_service.calculate_match_score(
            candidate_profile=profile_c,
            job_posting=python_posting,
        )

        if result_zero.overall_score is not None:
            raise RuntimeError(
                "Expected overall_score=None for a candidate with "
                f"no skills, got {result_zero.overall_score}"
            )

        if not result_zero.zero_skills_message:
            raise RuntimeError("Expected a zero_skills_message.")

        print("Zero-Skills Case Returns None (Not 0.0)        : Passed")

        # ---------------------------------------------------------
        # 3. Smoke test against real data already in the database.
        # ---------------------------------------------------------

        real_posting = session.scalar(select(JobPosting).limit(1))

        if real_posting is None:
            raise RuntimeError(
                "No job postings exist. Run a job import first."
            )

        result_real = matching_service.calculate_match_score(
            candidate_profile=profile_a,
            job_posting=real_posting,
        )

        if result_real.overall_score is None:
            raise RuntimeError(
                "Expected a numeric score for a candidate with "
                "skills, got None."
            )

        print("Real Posting Smoke Test (No Crash)             : Passed")

        smartrecruiters_source = session.scalar(
            select(Source).where(Source.name == "SmartRecruiters")
        )

        if smartrecruiters_source is not None:
            no_description_posting = session.scalar(
                select(JobPosting)
                .where(
                    JobPosting.source_id == smartrecruiters_source.id,
                    JobPosting.description.is_(None),
                )
                .limit(1)
            )

            if no_description_posting is not None:
                result_no_desc = matching_service.calculate_match_score(
                    candidate_profile=profile_a,
                    job_posting=no_description_posting,
                )

                if result_no_desc.overall_score is None:
                    raise RuntimeError(
                        "Title-only posting should still produce a "
                        "numeric score, got None."
                    )

                print(
                    "Title-Only Posting (No Description)            : "
                    "Passed"
                )
            else:
                print(
                    "Title-Only Posting (No Description)            : "
                    "Skipped (none found)"
                )
        else:
            print(
                "Title-Only Posting (No Description)            : "
                "Skipped (SmartRecruiters source not seeded)"
            )

        # ---------------------------------------------------------
        # 4. API route test -- the layer that previously had the
        #    profile-lookup bug. Includes a brand-new user who has
        #    never created a candidate profile, the exact scenario
        #    that crashed before this fix.
        # ---------------------------------------------------------

        client = TestClient(app)

        headers_a = {
            "Authorization": f"Bearer {create_access_token(user_a.id)}",
        }

        route_response = client.get(
            f"/jobs/{real_posting.id}/match-score",
            headers=headers_a,
        )

        if route_response.status_code != 200:
            raise RuntimeError(
                "GET /jobs/{id}/match-score failed for an "
                f"authenticated user: {route_response.status_code} "
                f"{route_response.text}"
            )

        if "overall_score" not in route_response.json():
            raise RuntimeError(
                "Match score API response missing overall_score."
            )

        print("API Route: GET /jobs/{id}/match-score          : Passed")

        brand_new_user = User(
            name="Brand New Matching User",
            email=new_user_email,
            password_hash="test_hash",
        )
        session.add(brand_new_user)
        session.commit()
        session.refresh(brand_new_user)

        headers_new = {
            "Authorization": (
                f"Bearer {create_access_token(brand_new_user.id)}"
            ),
        }

        new_user_response = client.get(
            f"/jobs/{real_posting.id}/match-score",
            headers=headers_new,
        )

        if new_user_response.status_code != 200:
            raise RuntimeError(
                "Match score endpoint failed for a user with no "
                "prior candidate profile (lazy-creation regression): "
                f"{new_user_response.status_code} "
                f"{new_user_response.text}"
            )

        print("API Route: Lazy Profile Creation On First Use  : Passed")

        print()
        print("Job matching service test passed.")

    finally:
        for email in (
            user_a_email,
            user_b_email,
            user_c_email,
            new_user_email,
        ):
            _clean_up_user(session, email)

        session.close()


if __name__ == "__main__":
    main()