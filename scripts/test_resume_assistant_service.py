"""
Test Resume Assistant Service

Integration test for ResumeAssistantService (Phase 7): the fixed-
template cover-letter draft and the skill-emphasis wrapper around
Phase 5's JobMatchingService.

Also tests the GET /jobs/{job_posting_id}/cover-letter-draft API
endpoint directly through a real authenticated request -- including
a brand-new user who has never created a candidate profile, the
exact scenario that broke Phase 5's endpoint before its lazy-
creation fix.

Zero-cost constraint check: nothing in this feature performs an LLM
call, runs a local model, or contacts any third-party AI service.
The draft is a deterministic template fill of real profile data.
"""

from datetime import date

import app.models  # noqa: F401

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_work_experience import (
    CandidateWorkExperience,
)
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.models.user import User
from app.services.job_matching_service import JobMatchingService
from app.services.resume_assistant_service import (
    COVER_LETTER_DRAFT_NOTE,
    ResumeAssistantService,
)


FULL_EMAIL = "resume_test_full@example.com"
NO_EXP_EMAIL = "resume_test_no_exp@example.com"
ZERO_SKILLS_EMAIL = "resume_test_zero_skills@example.com"
BRAND_NEW_EMAIL = "resume_test_brand_new@example.com"

COMPANY_NAME = "Resume Assistant Test Company"
SOURCE_NAME = "Resume Assistant Test Source"
POSTING_URL = "https://example.com/resume-assistant-test-job"


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


def _create_user_with_profile(
    session,
    email: str,
    name: str,
    skills: list[str],
    experiences: list[dict],
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

    for experience in experiences:
        session.add(
            CandidateWorkExperience(
                candidate_profile_id=profile.id,
                company_name=experience["company_name"],
                job_title=experience.get("job_title"),
                start_date=experience["start_date"],
                end_date=experience.get("end_date"),
                description=experience.get("description"),
            )
        )

    session.commit()
    session.refresh(profile)

    return user, profile


def _create_test_posting(session) -> JobPosting:
    source = (
        session.query(Source).filter(Source.name == SOURCE_NAME).first()
    )

    if source is None:
        source = Source(
            name=SOURCE_NAME,
            base_url="https://example.com",
            scraper_name="resume_assistant_test",
        )
        session.add(source)
        session.flush()

    existing_company = (
        session.query(Company).filter(Company.name == COMPANY_NAME).first()
    )

    if existing_company is not None:
        company = existing_company
    else:
        company = Company(name=COMPANY_NAME)
        session.add(company)
        session.flush()

    job = Job(
        company_id=company.id,
        title="Python Developer",
    )
    session.add(job)
    session.flush()

    posting = JobPosting(
        job_id=job.id,
        source_id=source.id,
        external_job_id="resume-assistant-test-1",
        posting_url=POSTING_URL,
        title="Senior Python Developer",
        location=None,
        work_mode="UNKNOWN",
        description=(
            "We are hiring a Senior Python Developer. "
            "Docker experience is a plus."
        ),
    )
    session.add(posting)
    session.commit()
    session.refresh(posting)

    return posting


def _delete_test_posting(session) -> None:
    posting = (
        session.query(JobPosting)
        .filter(JobPosting.posting_url == POSTING_URL)
        .first()
    )

    if posting is None:
        return

    job = session.get(Job, posting.job_id)
    company = job.company if job is not None else None
    source = (
        session.query(Source).filter(Source.name == SOURCE_NAME).first()
    )

    session.delete(posting)

    if job is not None:
        session.delete(job)

    if company is not None:
        session.delete(company)

    if source is not None:
        session.delete(source)

    session.commit()


def main() -> None:
    session = SessionLocal()

    try:
        for email in (
            FULL_EMAIL,
            NO_EXP_EMAIL,
            ZERO_SKILLS_EMAIL,
            BRAND_NEW_EMAIL,
        ):
            _clean_up_user(session, email)

        user_full, profile_full = _create_user_with_profile(
            session,
            FULL_EMAIL,
            "Full Data Candidate",
            ["Python", "Docker"],
            [
                {
                    "company_name": "TechCorp",
                    "job_title": "QA Engineer",
                    "start_date": date(2021, 3, 1),
                    "end_date": None,
                    "description": None,
                },
                {
                    "company_name": "OldCorp",
                    "job_title": "Intern",
                    "start_date": date(2018, 6, 1),
                    "end_date": date(2019, 6, 1),
                    "description": None,
                },
            ],
        )
        _, profile_no_exp = _create_user_with_profile(
            session,
            NO_EXP_EMAIL,
            "No Experience Candidate",
            ["Python", "Docker"],
            [],
        )
        _, profile_zero_skills = _create_user_with_profile(
            session,
            ZERO_SKILLS_EMAIL,
            "Zero Skills Candidate",
            [],
            [
                {
                    "company_name": "SoloStudio",
                    "job_title": "Founder",
                    "start_date": date(2020, 1, 1),
                    "end_date": None,
                    "description": None,
                }
            ],
        )

        python_posting = JobPosting(
            title="Senior Python Developer",
            description=(
                "You will build services in Python. "
                "Docker experience is a plus."
            ),
            location=None,
            work_mode="UNKNOWN",
            posting_url="https://example.com/resume-test-synthetic-job",
        )

        resume_service = ResumeAssistantService()

        print()
        print("# Resume Assistant Service Test")
        print()

        # ---------------------------------------------------------
        # 1. Full-data candidate: work experience + matched skills.
        # ---------------------------------------------------------

        emphasis_full = resume_service.get_skill_emphasis(
            candidate_profile=profile_full,
            job_posting=python_posting,
        )

        if set(emphasis_full) != {"Python", "Docker"} or len(
            emphasis_full
        ) != 2:
            raise RuntimeError(
                "Expected exactly Python and Docker as skill "
                f"emphasis, got {emphasis_full}"
            )

        draft_full = resume_service.generate_cover_letter_draft(
            candidate_name=user_full.name,
            candidate_profile=profile_full,
            job_posting=python_posting,
            company_name="Example Robotics",
        )

        expected_fragments = [
            "Dear Hiring Team,",
            "the Senior Python Developer position at Example Robotics.",
            "In my most recent role as QA Engineer at TechCorp, "
            "I gained experience that I believe is directly relevant "
            "to this opportunity.",
            "my experience with Python and Docker aligns well",
            "Sincerely,",
            "Full Data Candidate",
        ]

        for fragment in expected_fragments:
            if fragment not in draft_full:
                raise RuntimeError(
                    f"Expected fragment missing from draft: {fragment!r}\n"
                    f"--- draft ---\n{draft_full}"
                )

        if "OldCorp" in draft_full:
            raise RuntimeError(
                "Draft used a non-most-recent experience entry "
                "(OldCorp found; TechCorp expected)."
            )

        if "{" in draft_full or "}" in draft_full:
            raise RuntimeError(
                "Draft contains literal brace placeholders -- an "
                f"unfilled template leaked through:\n{draft_full}"
            )

        if not draft_full.endswith(
            "Sincerely,\nFull Data Candidate"
        ):
            raise RuntimeError(
                "Draft does not end with the candidate signature.\n"
                f"--- draft ---\n{draft_full}"
            )

        print("Template Fill (Experience + Skills)          : Passed")
        print("No Literal Placeholders In Draft             : Passed")

        # ---------------------------------------------------------
        # 2. Parity regression: get_skill_emphasis must return
        #    exactly what JobMatchingService returns independently.
        # ---------------------------------------------------------

        independent_result = JobMatchingService().calculate_match_score(
            candidate_profile=profile_full,
            job_posting=python_posting,
        )

        if emphasis_full != independent_result.matched_skills:
            raise RuntimeError(
                "get_skill_emphasis drifted from "
                "JobMatchingService.calculate_match_score: "
                f"{emphasis_full} != {independent_result.matched_skills}"
            )

        print("Skill Emphasis Parity With Matching Service  : Passed")

        # ---------------------------------------------------------
        # 3. Candidate with no work experience at all.
        # ---------------------------------------------------------

        draft_no_exp = resume_service.generate_cover_letter_draft(
            candidate_name="No Experience Candidate",
            candidate_profile=profile_no_exp,
            job_posting=python_posting,
            company_name="Example Robotics",
        )

        if "In my most recent role" in draft_no_exp:
            raise RuntimeError(
                "Experience paragraph appeared despite the profile "
                "having no work experience."
            )

        for fragment in (
            "Dear Hiring Team,",
            "the Senior Python Developer position at Example Robotics.",
            "my experience with Python and Docker aligns well",
            "Sincerely,\nNo Experience Candidate",
        ):
            if fragment not in draft_no_exp:
                raise RuntimeError(
                    f"Expected fragment missing from no-experience "
                    f"draft: {fragment!r}\n--- draft ---\n{draft_no_exp}"
                )

        if "{" in draft_no_exp or "}" in draft_no_exp:
            raise RuntimeError(
                "No-experience draft contains literal placeholders:\n"
                f"{draft_no_exp}"
            )

        print("Graceful Degradation (No Work Experience)    : Passed")

        # ---------------------------------------------------------
        # 4. Zero-skills candidate (Phase 5 zero-skills case).
        # ---------------------------------------------------------

        emphasis_zero = resume_service.get_skill_emphasis(
            candidate_profile=profile_zero_skills,
            job_posting=python_posting,
        )

        if emphasis_zero != []:
            raise RuntimeError(
                "Expected an empty skill-emphasis list for a "
                f"candidate with zero skills, got {emphasis_zero}"
            )

        draft_zero = resume_service.generate_cover_letter_draft(
            candidate_name="Zero Skills Candidate",
            candidate_profile=profile_zero_skills,
            job_posting=python_posting,
            company_name="Example Robotics",
        )

        if "In particular," in draft_zero:
            raise RuntimeError(
                "Skills paragraph appeared despite zero matched "
                "skills."
            )

        if "role as Founder at SoloStudio" not in draft_zero:
            raise RuntimeError(
                "Experience paragraph missing for zero-skills "
                f"candidate who has one:\n{draft_zero}"
            )

        for fragment in (
            "Dear Hiring Team,",
            "Sincerely,\nZero Skills Candidate",
        ):
            if fragment not in draft_zero:
                raise RuntimeError(
                    f"Expected fragment missing from zero-skills "
                    f"draft: {fragment!r}\n--- draft ---\n{draft_zero}"
                )

        if "{" in draft_zero or "}" in draft_zero:
            raise RuntimeError(
                "Zero-skills draft contains literal placeholders:\n"
                f"{draft_zero}"
            )

        print("Zero-Skills Case Returns [] And Valid Letter : Passed")

        # ---------------------------------------------------------
        # 5. API route tests via TestClient, including the brand-new
        #    user scenario that previously broke Phase 5's endpoint.
        # ---------------------------------------------------------

        posting = _create_test_posting(session)

        client = TestClient(app)

        unauthenticated_response = client.get(
            f"/jobs/{posting.id}/cover-letter-draft",
        )

        if unauthenticated_response.status_code != 401:
            raise RuntimeError(
                "Expected 401 for unauthenticated cover-letter-draft "
                "request, got "
                f"{unauthenticated_response.status_code}"
            )

        print("API Route: Unauthenticated Request Is 401     : Passed")

        headers_full = {
            "Authorization": (
                f"Bearer {create_access_token(user_full.id)}"
            ),
        }

        api_response = client.get(
            f"/jobs/{posting.id}/cover-letter-draft",
            headers=headers_full,
        )

        if api_response.status_code != 200:
            raise RuntimeError(
                "GET /jobs/{id}/cover-letter-draft failed for an "
                f"authenticated user: {api_response.status_code} "
                f"{api_response.text}"
            )

        payload = api_response.json()

        for field in ("job_posting_id", "draft_text", "skill_emphasis"):
            if field not in payload:
                raise RuntimeError(
                    f"Cover-letter API response missing {field}."
                )

        if payload["note"] != COVER_LETTER_DRAFT_NOTE:
            raise RuntimeError(
                "Cover-letter API response note does not match the "
                "service-level disclaimer constant."
            )

        if payload["skill_emphasis"] != emphasis_full:
            raise RuntimeError(
                "API skill_emphasis differs from service output: "
                f"{payload['skill_emphasis']} != {emphasis_full}"
            )

        if "{" in payload["draft_text"] or "}" in payload["draft_text"]:
            raise RuntimeError(
                "API draft_text contains literal placeholders:\n"
                f"{payload['draft_text']}"
            )

        if user_full.name not in payload["draft_text"]:
            raise RuntimeError(
                "API draft_text does not contain the candidate name."
            )

        print("API Route: GET /jobs/{id}/cover-letter-draft : Passed")

        brand_new_user = User(
            name="Brand New Resume User",
            email=BRAND_NEW_EMAIL,
            password_hash="test_hash",
        )
        session.add(brand_new_user)
        session.commit()
        session.refresh(brand_new_user)

        pre_request_profile = (
            session.query(CandidateProfile)
            .filter(
                CandidateProfile.user_id == brand_new_user.id
            )
            .first()
        )

        if pre_request_profile is not None:
            raise RuntimeError(
                "Test setup error: brand-new user unexpectedly "
                "already has a candidate profile."
            )

        headers_new = {
            "Authorization": (
                f"Bearer {create_access_token(brand_new_user.id)}"
            ),
        }

        new_user_response = client.get(
            f"/jobs/{posting.id}/cover-letter-draft",
            headers=headers_new,
        )

        if new_user_response.status_code != 200:
            raise RuntimeError(
                "Cover-letter endpoint failed for a user with no "
                "prior candidate profile (lazy-creation regression): "
                f"{new_user_response.status_code} "
                f"{new_user_response.text}"
            )

        new_payload = new_user_response.json()

        if new_payload["skill_emphasis"] != []:
            raise RuntimeError(
                "Expected empty skill emphasis for a brand-new "
                f"user, got {new_payload['skill_emphasis']}"
            )

        post_request_profile = (
            session.query(CandidateProfile)
            .filter(
                CandidateProfile.user_id == brand_new_user.id
            )
            .first()
        )

        if post_request_profile is None:
            raise RuntimeError(
                "Candidate profile was not lazily created by the "
                "cover-letter endpoint for a first-time user."
            )

        print("API Route: Lazy Profile Creation On First Use : Passed")

        missing_response = client.get(
            "/jobs/99999999/cover-letter-draft",
            headers=headers_full,
        )

        if missing_response.status_code != 404:
            raise RuntimeError(
                "Expected 404 for a nonexistent posting, got "
                f"{missing_response.status_code}"
            )

        print("API Route: Missing Posting Is 404             : Passed")

        print()
        print("Resume assistant service test passed.")

    finally:
        _delete_test_posting(session)

        for email in (
            FULL_EMAIL,
            NO_EXP_EMAIL,
            ZERO_SKILLS_EMAIL,
            BRAND_NEW_EMAIL,
        ):
            _clean_up_user(session, email)

        session.close()


if __name__ == "__main__":
    main()
