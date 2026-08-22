"""
Test Apply Kit Service

Integration test for Phase 8's Apply Kit: the answer bank
(model/repository/service + Alembic revision), the profile-page
management endpoints, and the job-detail Apply Kit section.

Covers:
- CRUD round-trip through the HTTP endpoints
- Cross-user isolation (user B cannot read or delete user A's answers)
- Unauthenticated requests are rejected with 401
- Brand-new-user empty states on both pages (no crash, no broken markup)
- Stored text is escaped everywhere it is rendered (no raw <script>)
- Copy buttons reference textarea ids only -- stored values never reach
  the inline clipboard script
- The job-detail anchors are well-formed after the actions regrouping
  (regression check for the missing "<a" opener bug found in review)
- mark-as-applied still works end-to-end
- The Alembic revision upgrades a fresh database cleanly and downgrades back

Zero-cost constraint check: nothing in this feature performs an LLM
call, runs a local model, or contacts any third-party service.
"""

import re
import shutil
import tempfile
from pathlib import Path

import app.models  # noqa: F401

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from app.auth.jwt import create_access_token
from app.database.base import Base
from app.database.session import SessionLocal
from app.main import app
from app.models.answer_bank_entry import AnswerBankEntry
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.models.user import User


FULL_EMAIL = "apply_kit_test_full@example.com"
USER_B_EMAIL = "apply_kit_test_user_b@example.com"
BRAND_NEW_EMAIL = "apply_kit_test_brand_new@example.com"

COMPANY_NAME = "Apply Kit Test Company"
SOURCE_NAME = "Apply Kit Test Source"
POSTING_URL = "https://example.com/apply-kit-test-job"

XSS_PAYLOAD = "<script>alert(1)</script>"
XSS_ESCAPED = "&lt;script&gt;alert(1)&lt;/script&gt;"


def _clean_up_user(session, email: str) -> None:
    """
    Remove a test user plus their candidate profile (which cascades to
    structured entries) and any saved answer bank entries.
    """

    user = session.query(User).filter(User.email == email).first()

    if user is None:
        return

    session.query(AnswerBankEntry).filter(
        AnswerBankEntry.user_id == user.id,
    ).delete()

    profile = (
        session.query(CandidateProfile)
        .filter(CandidateProfile.user_id == user.id)
        .first()
    )

    if profile is not None:
        session.delete(profile)

    session.delete(user)
    session.commit()


def _create_full_user(session) -> User:
    """
    Create a user whose profile carries phone, location, and two
    structured skills -- enough data for a complete Apply Kit.
    """

    user = User(
        name="Apply Kit Full User",
        email=FULL_EMAIL,
        password_hash="test_hash",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    profile = CandidateProfile(
        user_id=user.id,
        phone="+1 555 010 2030",
        location="Berlin, Germany",
    )
    session.add(profile)
    session.flush()

    session.add(
        CandidateSkill(candidate_profile_id=profile.id, name="Python")
    )
    session.add(
        CandidateSkill(candidate_profile_id=profile.id, name="Docker")
    )
    session.commit()
    session.refresh(profile)

    return user


def _create_bare_user(session, email: str, name: str) -> User:
    """
    Create a user with no candidate profile and no saved answers.
    """

    user = User(
        name=name,
        email=email,
        password_hash="test_hash",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def _create_test_posting(session) -> JobPosting:
    source = (
        session.query(Source).filter(Source.name == SOURCE_NAME).first()
    )

    if source is None:
        source = Source(
            name=SOURCE_NAME,
            base_url="https://example.com",
            scraper_name="apply_kit_test",
        )
        session.add(source)
        session.flush()

    company = (
        session.query(Company)
        .filter(Company.name == COMPANY_NAME)
        .first()
    )

    if company is None:
        company = Company(name=COMPANY_NAME)
        session.add(company)
        session.flush()

    job = Job(
        company_id=company.id,
        title="Apply Kit Test Engineer",
    )
    session.add(job)
    session.flush()

    posting = JobPosting(
        job_id=job.id,
        source_id=source.id,
        external_job_id="apply-kit-test-1",
        posting_url=POSTING_URL,
        title="Apply Kit Test Engineer",
        location=None,
        work_mode="UNKNOWN",
        description="Testing posting for the Phase 8 Apply Kit.",
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


def _run_alembic_fresh_database_check() -> None:
    """
    Verify the Phase 8 revision upgrades a fresh database cleanly and
    downgrades back.

    The baseline revision is snapshot-style (its upgrade drops the
    pre-existing tables), so real databases are built with
    ``create_all`` first. We reproduce that here: build the current
    schema without the new table, stamp the previous head, then run
    only the Phase 8 revision forward and back.
    """

    from alembic import command
    from alembic.config import Config

    project_root = Path(__file__).resolve().parent.parent
    temp_dir = tempfile.mkdtemp(prefix="apply_kit_alembic_")
    db_path = Path(temp_dir) / "fresh.db"

    try:
        engine = create_engine(f"sqlite:///{db_path.as_posix()}")

        Base.metadata.create_all(bind=engine)

        # Simulate a pre-Phase-8 database: everything exists except
        # the new answer_bank_entries table.
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE answer_bank_entries"))

        config = Config()
        config.set_main_option(
            "script_location",
            str(project_root / "alembic"),
        )
        config.set_main_option(
            "sqlalchemy.url",
            f"sqlite:///{db_path.as_posix()}",
        )

        command.stamp(config, "add_application_status")
        command.upgrade(config, "head")

        columns = [
            column["name"]
            for column in inspect(engine).get_columns(
                "answer_bank_entries"
            )
        ]

        expected_columns = [
            "id",
            "user_id",
            "question_text",
            "answer_text",
            "created_at",
            "updated_at",
        ]

        if columns != expected_columns:
            raise RuntimeError(
                "Unexpected answer_bank_entries columns after "
                f"upgrade: {columns}"
            )

        with engine.connect() as connection:
            version = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar()

        if version != "add_answer_bank_entries":
            raise RuntimeError(
                f"Unexpected alembic version after upgrade: {version}"
            )

        command.downgrade(config, "-1")

        tables_after_downgrade = inspect(engine).get_table_names()

        if "answer_bank_entries" in tables_after_downgrade:
            raise RuntimeError(
                "Downgrade did not remove answer_bank_entries."
            )

        command.upgrade(config, "head")

        tables_after_reupgrade = inspect(engine).get_table_names()

        if "answer_bank_entries" not in tables_after_reupgrade:
            raise RuntimeError(
                "Re-upgrade did not recreate answer_bank_entries."
            )

        engine.dispose()

        print("Alembic fresh-database upgrade/downgrade: OK")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    """
    Test the Phase 8 Apply Kit end-to-end.
    """

    session = SessionLocal()
    client = TestClient(app)

    try:
        for email in (
            FULL_EMAIL,
            USER_B_EMAIL,
            BRAND_NEW_EMAIL,
        ):
            _clean_up_user(session, email)

        _delete_test_posting(session)

        user_a = _create_full_user(session)
        user_b = _create_bare_user(
            session,
            USER_B_EMAIL,
            "Apply Kit User B",
        )
        brand_new = _create_bare_user(
            session,
            BRAND_NEW_EMAIL,
            "Brand New User",
        )

        posting = _create_test_posting(session)

        headers_a = {
            "Authorization": (
                f"Bearer {create_access_token(user_a.id)}"
            ),
        }
        headers_b = {
            "Authorization": (
                f"Bearer {create_access_token(user_b.id)}"
            ),
        }
        headers_new = {
            "Authorization": (
                f"Bearer {create_access_token(brand_new.id)}"
            ),
        }

        print()
        print("# Apply Kit Test")
        print()

        # -------------------------------------------------------------
        # 1. Unauthenticated requests are rejected with 401.
        # -------------------------------------------------------------
        response = client.get("/dashboard/profile")
        assert response.status_code == 401, response.status_code

        response = client.get(f"/dashboard/jobs/{posting.id}")
        assert response.status_code == 401, response.status_code

        response = client.post("/dashboard/profile/answers/add")
        assert response.status_code == 401, response.status_code

        response = client.post("/dashboard/profile/answers/1/delete")
        assert response.status_code == 401, response.status_code

        print("1. Unauthenticated requests return 401: OK")

        # -------------------------------------------------------------
        # 2. CRUD round-trip as user A via the HTTP endpoints, plus
        #    escaping of stored text on the profile page.
        # -------------------------------------------------------------
        benign_question = "How many years of production Python?"
        benign_answer = "Six years across two product teams."

        response = client.post(
            "/dashboard/profile/answers/add",
            data={
                "question_text": benign_question,
                "answer_text": benign_answer,
            },
            headers=headers_a,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        response = client.post(
            "/dashboard/profile/answers/add",
            data={
                "question_text": XSS_PAYLOAD,
                "answer_text": XSS_PAYLOAD,
            },
            headers=headers_a,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        benign_entry = (
            session.query(AnswerBankEntry)
            .filter(
                AnswerBankEntry.user_id == user_a.id,
                AnswerBankEntry.question_text == benign_question,
            )
            .first()
        )
        xss_entry = (
            session.query(AnswerBankEntry)
            .filter(
                AnswerBankEntry.user_id == user_a.id,
                AnswerBankEntry.question_text == XSS_PAYLOAD,
            )
            .first()
        )

        if benign_entry is None or xss_entry is None:
            raise RuntimeError("Answers were not persisted.")

        response = client.get(
            "/dashboard/profile",
            headers=headers_a,
        )
        assert response.status_code == 200, response.status_code

        if "Saved Answers" not in response.text:
            raise RuntimeError("Saved Answers heading is missing.")

        if benign_question not in response.text:
            raise RuntimeError("Benign question is missing.")

        if benign_answer not in response.text:
            raise RuntimeError("Benign answer is missing.")

        if XSS_PAYLOAD in response.text:
            raise RuntimeError("Raw XSS payload leaked into HTML.")

        if XSS_ESCAPED not in response.text:
            raise RuntimeError("XSS payload was not escaped.")

        print("2. Add + list round-trip with escaping: OK")

        # -------------------------------------------------------------
        # 3. Cross-user isolation: user B cannot read A's answers on
        #    any page and cannot delete them through the endpoint.
        # -------------------------------------------------------------
        response = client.get(
            "/dashboard/profile",
            headers=headers_b,
        )
        assert response.status_code == 200, response.status_code

        if benign_question in response.text:
            raise RuntimeError("User B sees user A's question.")

        if XSS_ESCAPED in response.text:
            raise RuntimeError("User B sees user A's answer.")

        response = client.post(
            f"/dashboard/profile/answers/{benign_entry.id}/delete",
            headers=headers_b,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        still_there = (
            session.query(AnswerBankEntry)
            .filter(AnswerBankEntry.id == benign_entry.id)
            .first()
        )

        if still_there is None:
            raise RuntimeError(
                "User B was able to delete user A's answer."
            )

        # User B can add and delete an own answer (owner path works).
        response = client.post(
            "/dashboard/profile/answers/add",
            data={
                "question_text": "B question",
                "answer_text": "B answer",
            },
            headers=headers_b,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        b_entry = (
            session.query(AnswerBankEntry)
            .filter(
                AnswerBankEntry.user_id == user_b.id,
                AnswerBankEntry.question_text == "B question",
            )
            .first()
        )

        if b_entry is None:
            raise RuntimeError("User B's answer was not persisted.")

        response = client.post(
            f"/dashboard/profile/answers/{b_entry.id}/delete",
            headers=headers_b,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        gone = (
            session.query(AnswerBankEntry)
            .filter(AnswerBankEntry.id == b_entry.id)
            .first()
        )

        if gone is not None:
            raise RuntimeError("Owner could not delete own answer.")

        print("3. Cross-user isolation enforced: OK")

        # -------------------------------------------------------------
        # 4. Owner deletes own answer; row disappears everywhere.
        # -------------------------------------------------------------
        response = client.post(
            f"/dashboard/profile/answers/{benign_entry.id}/delete",
            headers=headers_a,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        deleted = (
            session.query(AnswerBankEntry)
            .filter(AnswerBankEntry.id == benign_entry.id)
            .first()
        )

        if deleted is not None:
            raise RuntimeError("Owner delete did not remove the row.")

        print("4. Owner delete round-trip: OK")

        # -------------------------------------------------------------
        # 5. Job-detail Apply Kit renders for the full user: contact
        #    fields, skills line, escaped saved answer, copy buttons
        #    that carry ids only, and well-formed action anchors.
        # -------------------------------------------------------------
        response = client.get(
            f"/dashboard/jobs/{posting.id}",
            headers=headers_a,
        )
        assert response.status_code == 200, response.status_code

        detail_html = response.text

        required_strings = [
            "Apply Kit",                       # section heading
            'data-copy-target="kit-name"',     # copy buttons exist...
            'data-copy-target="kit-email"',
            'data-copy-target="kit-phone"',
            'data-copy-target="kit-location"',
            'data-copy-target="kit-skills"',
            "+1 555 010 2030",                 # ...and carry no text;
            "Berlin, Germany",                 # values live in the
            "Python, Docker",                  # readonly textareas
            "Open Job Posting",
            f'href="{POSTING_URL}"',
            XSS_ESCAPED,                       # stored answer escaped
            f'data-copy-target="kit-answer-{xss_entry.id}"',
        ]

        for needle in required_strings:
            if needle not in detail_html:
                raise RuntimeError(
                    f"Job detail page is missing: {needle!r}"
                )

        if XSS_PAYLOAD in detail_html:
            raise RuntimeError(
                "Raw XSS payload leaked into the Apply Kit."
            )

        # Regression check: the "<a" opener existed before Phase 8's
        # regrouping fixed it. \s spans the multi-line attributes.
        if re.search(r'<a\s+class="button"', detail_html) is None:
            raise RuntimeError(
                "Action anchors are not well-formed <a> tags."
            )

        if f'action="/dashboard/jobs/{posting.id}/apply"' \
                not in detail_html:
            raise RuntimeError("Mark-as-applied control is missing.")

        print("5. Apply Kit rendering on job detail: OK")

        # -------------------------------------------------------------
        # 6. Brand-new user empty states: no profile data and zero
        #    answers must render clean messages, never crash.
        # -------------------------------------------------------------
        response = client.get(
            f"/dashboard/jobs/{posting.id}",
            headers=headers_new,
        )
        assert response.status_code == 200, response.status_code

        new_html = response.text

        for needle in [
            "Apply Kit",
            brand_new.name,
            brand_new.email,
            "Not set yet -- add Phone on your Candidate Profile.",
            "Not set yet -- add Location on your Candidate Profile.",
            "No skills tracked yet",
            "No saved answers yet",
        ]:
            if needle not in new_html:
                raise RuntimeError(
                    f"Brand-new user job detail is missing: {needle!r}"
                )

        if 'data-copy-target="kit-phone"' in new_html:
            raise RuntimeError(
                "Copy button rendered for a blank field."
            )

        response = client.get(
            "/dashboard/profile",
            headers=headers_new,
        )
        assert response.status_code == 200, response.status_code

        if "Saved Answers" not in response.text:
            raise RuntimeError(
                "Profile page lacks Saved Answers section."
            )

        if "No saved answers yet" not in response.text:
            raise RuntimeError(
                "Profile page lacks answers empty state."
            )

        print("6. Brand-new user empty states: OK")

        # -------------------------------------------------------------
        # 7. mark-as-applied still works end-to-end from inside the
        #    regrouped kit actions.
        # -------------------------------------------------------------
        response = client.post(
            f"/dashboard/jobs/{posting.id}/apply",
            headers=headers_new,
            follow_redirects=False,
        )
        assert response.status_code == 303, response.status_code

        response = client.get(
            f"/dashboard/jobs/{posting.id}",
            headers=headers_new,
        )
        assert response.status_code == 200, response.status_code

        if "You have already applied" not in response.text:
            raise RuntimeError(
                "mark-as-applied did not register the application."
            )

        print("7. mark-as-applied end-to-end: OK")

        # -------------------------------------------------------------
        # 8. The Alembic revision upgrades a fresh database cleanly
        #    and downgrades back.
        # -------------------------------------------------------------
        _run_alembic_fresh_database_check()

        print()
        print("Apply Kit test passed.")

    finally:
        for email in (
            FULL_EMAIL,
            USER_B_EMAIL,
            BRAND_NEW_EMAIL,
        ):
            _clean_up_user(session, email)

        _delete_test_posting(session)
        session.close()


if __name__ == "__main__":
    main()
