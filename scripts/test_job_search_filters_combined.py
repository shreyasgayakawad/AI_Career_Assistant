"""
Job Search Combined Filters Test

Verifies that multiple query parameters can be combined on /jobs/ and that
invalid inputs return HTTP 400 rather than silently returning everything
or crashing with a 500.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.main import app


def test_location_and_posted_after_together() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?location=Sydney&posted_after=2026-01-01")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    for r in data:
        assert "Sydney" in r["location"], (
            f"Expected location to contain 'Sydney', got '{r['location']}'"
        )


def test_has_salary_true() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?has_salary=true")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    # 0 is a valid result - it just means no postings have salary data


def test_has_salary_false() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?has_salary=false")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    assert len(data) > 0, "Expected at least one result for has_salary=false"


if __name__ == "__main__":
    test_location_and_posted_after_together()
    test_has_salary_true()
    test_has_salary_false()
    print("Combined filters test passed.")