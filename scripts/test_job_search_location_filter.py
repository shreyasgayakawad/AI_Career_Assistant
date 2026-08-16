"""
Job Search Location Filter Test

Verifies that the /jobs/ location query parameter correctly narrows results.
"""

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from fastapi.testclient import TestClient

from app.main import app


def test_location_filter() -> None:
    client = TestClient(app)

    resp = client.get("/jobs/?location=Sydney")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    assert len(data) > 0, "Expected at least one result for Sydney"

    for r in data:
        assert "Sydney" in r["location"], (
            f"Expected location to contain 'Sydney', got '{r['location']}'"
        )


if __name__ == "__main__":
    test_location_filter()
    print("Location filter test passed.")