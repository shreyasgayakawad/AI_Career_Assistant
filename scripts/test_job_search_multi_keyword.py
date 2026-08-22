"""
Test Multi-Keyword Job Search

Regression test for multi-keyword search on job postings: a keyword
such as "cloud support" must match postings whose title/description
contain all tokens regardless of word order or which field each
token appears in -- not only when the exact phrase occurs
contiguously.

Also exercises the public GET /jobs endpoint end-to-end so the
dashboard search box behavior is covered at the HTTP layer.
"""

import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.source import Source
from app.repositories.job_posting_repository import (
    JobPostingRepository,
)


SOURCE_NAME = "Multi Keyword Search Source"
COMPANY_NAME = "Multi Keyword Search Co"

SEED_POSTINGS = [
    {
        "key": "reordered",
        "title": "Support Engineer - Cloud Platform",
        "description": "Keep our customer platform healthy.",
    },
    {
        "key": "application",
        "title": "Application Cloud Support",
        "description": "Handle escalations and tooling.",
    },
    {
        "key": "canonical",
        "title": "Cloud Support Engineer",
        "description": "AWS and Azure environments.",
    },
    {
        "key": "cloud_only",
        "title": "DevOps Engineer",
        "description": "Cloud infrastructure and automation.",
    },
    {
        "key": "neither",
        "title": "Data Analyst",
        "description": "SQL reporting and dashboards.",
    },
    {
        "key": "cross_field",
        "title": "Support Specialist",
        "description": (
            "You will support internal tools on our cloud stack."
        ),
    },
]


def _seed(session) -> dict[str, int]:
    """
    Create an isolated company/source/job chain plus one posting per
    SEED_POSTINGS entry. Returns {key: posting_id}.
    """

    source = (
        session.query(Source).filter(Source.name == SOURCE_NAME).first()
    )

    if source is None:
        source = Source(
            name=SOURCE_NAME,
            base_url="https://example.com",
            scraper_name="multi_keyword_test",
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

    ids: dict[str, int] = {}

    for index, spec in enumerate(SEED_POSTINGS):
        job = Job(
            company_id=company.id,
            title=spec["title"],
        )
        session.add(job)
        session.flush()

        posting = JobPosting(
            job_id=job.id,
            source_id=source.id,
            external_job_id=f"multi-keyword-{index}",
            posting_url=(
                f"https://example.com/multi-keyword-search/{index}"
            ),
            title=spec["title"],
            location=None,
            work_mode="UNKNOWN",
            description=spec["description"],
            status="ACTIVE",
        )
        session.add(posting)
        session.flush()

        ids[spec["key"]] = posting.id

    session.commit()

    return ids


def _cleanup(session) -> None:
    postings = (
        session.query(JobPosting)
        .filter(
            JobPosting.posting_url.like(
                "https://example.com/multi-keyword-search/%"
            )
        )
        .all()
    )

    for posting in postings:
        job = session.get(Job, posting.job_id)
        session.delete(posting)

        if job is not None:
            session.delete(job)

    company = (
        session.query(Company)
        .filter(Company.name == COMPANY_NAME)
        .first()
    )

    if company is not None:
        session.delete(company)

    source = (
        session.query(Source).filter(Source.name == SOURCE_NAME).first()
    )

    if source is not None:
        session.delete(source)

    session.commit()


def _ids_for(repository, keyword: str | None) -> set[int]:
    results = repository.search(keyword=keyword)

    return {posting.id for posting in results}


def main() -> None:
    session = SessionLocal()

    try:
        seeded_ids = _seed(session)
        repository = JobPostingRepository(session)

        print()
        print("# Multi-Keyword Job Search Test")
        print()

        def expect(keyword: str | None, keys: list[str]) -> set[int]:
            expected = {seeded_ids[key] for key in keys}

            actual = _ids_for(repository, keyword)

            missing = expected - actual

            if missing:
                raise RuntimeError(
                    f"keyword={keyword!r} missed expected postings "
                    f"{missing}. Got {sorted(actual)}, expected "
                    f"{sorted(expected)}."
                )

            return actual

        # 1. The user's failing case: words in reverse order.
        result = expect("cloud support", ["reordered", "application",
                                          "canonical", "cross_field"])

        if seeded_ids["cloud_only"] in result:
            raise RuntimeError(
                "'cloud support' matched a posting containing "
                "'cloud' but not 'support' -- AND semantics broken."
            )

        if seeded_ids["neither"] in result:
            raise RuntimeError(
                "'cloud support' matched a posting with neither "
                "token."
            )

        print("Reverse-Order Tokens ('cloud support')       : Passed")

        # 2. Three keywords. The 'application' seed deliberately
        #    contains no 'engineer', so it must NOT match here.
        result = expect("cloud support engineer",
                        ["reordered", "canonical"])

        if seeded_ids["application"] in result:
            raise RuntimeError(
                "'cloud support engineer' matched a posting "
                "without the word 'engineer'."
            )

        print("Three Keywords ('cloud support engineer')    : Passed")

        # 3. The second example from the bug report.
        result = expect("application cloud support", ["application"])

        if seeded_ids["canonical"] in result:
            raise RuntimeError(
                "'application cloud support' matched a posting "
                "without the word 'application'."
            )

        print("Three Keywords ('application cloud ...')     : Passed")

        # 4. Cross-field matching: one token in title, the other
        #    only in the description.
        expect("support cloud", ["cross_field"])
        print("Tokens Split Across Fields                   : Passed")

        # 5. AND semantics: two absent tokens match nothing.
        result = expect("quantum blockchain", [])

        if result:
            raise RuntimeError(
                f"'quantum blockchain' unexpectedly matched: "
                f"{sorted(result)}"
            )

        print("Absent Tokens Match Nothing                  : Passed")

        # 6. Case-insensitivity and extra whitespace.
        expect("  CLOUD    Support  ",
               ["reordered", "application", "canonical", "cross_field"])
        print("Case-Insensitive + Extra Whitespace          : Passed")

        # 7. Single-keyword regression: unchanged behavior.
        result = expect("analyst", ["neither"])

        if seeded_ids["canonical"] in result:
            raise RuntimeError(
                "Single token 'analyst' matched an unrelated "
                "posting."
            )

        print("Single Keyword Regression                    : Passed")

        # 8. End-to-end through the public GET /jobs endpoint --
        #    the same service path the dashboard search box uses.
        client = TestClient(app)

        api_response = client.get(
            "/jobs/",
            params={"keyword": "cloud support"},
        )

        if api_response.status_code != 200:
            raise RuntimeError(
                "GET /jobs failed: "
                f"{api_response.status_code} {api_response.text}"
            )

        api_ids = {item["id"] for item in api_response.json()}

        for key in ("reordered", "application", "canonical",
                    "cross_field"):
            if seeded_ids[key] not in api_ids:
                raise RuntimeError(
                    f"API response missing seeded posting '{key}' "
                    f"for multi-keyword search."
                )

        for key in ("cloud_only", "neither"):
            if seeded_ids[key] in api_ids:
                raise RuntimeError(
                    f"API response included non-matching posting "
                    f"'{key}'."
                )

        print("API Route: GET /jobs?keyword=cloud+support   : Passed")

        print()
        print("Multi-keyword job search test passed.")

    finally:
        _cleanup(session)
        session.close()


if __name__ == "__main__":
    main()
