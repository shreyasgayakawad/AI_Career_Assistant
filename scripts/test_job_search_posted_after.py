"""
Job Search Posted-After Date Test

Verifies that the /jobs/ posted_after query parameter correctly narrows
results and rejects invalid date strings with HTTP 400.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.main import app


def test_posted_after_valid() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?posted_after=2026-01-01")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    assert len(data) > 0, "Expected at least one result for posted_after=2026-01-01"


def test_posted_after_invalid() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?posted_after=not-a-date")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"

    detail = resp.json().get("detail", "")
    assert "Invalid posted_after date" in detail, (
        f"Expected 'Invalid posted_after date' in detail, got '{detail}'"
    )


def test_posted_after_with_no_other_filters() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?posted_after=2024-01-01")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    assert len(data) > 0, "Expected at least one result for posted_after=2024-01-01"


if __name__ == "__main__":
    test_posted_after_valid()
    test_posted_after_invalid()
    test_posted_after_with_no_other_filters()
    print("Posted-after date test passed.")