"""
Test Job Posting Work Mode Backfill

Tests location-based work-mode classification.
"""

from scripts.migrate_job_posting_work_mode_backfill import (
    classify_work_mode,
)


def main() -> None:
    """
    Test work-mode classification.
    """

    # ---------------------------------------------------------------
    # REMOTE
    # ---------------------------------------------------------------

    assert (
        classify_work_mode("Remote")
        == "REMOTE"
    )

    assert (
        classify_work_mode(
            "Remote-Friendly, United States"
        )
        == "REMOTE"
    )

    assert (
        classify_work_mode(
            "Remote-Friendly (Travel-Required) | "
            "San Francisco, CA"
        )
        == "REMOTE"
    )

    # ---------------------------------------------------------------
    # HYBRID
    # ---------------------------------------------------------------

    assert (
        classify_work_mode(
            "Hybrid - San Francisco, CA"
        )
        == "HYBRID"
    )

    assert (
        classify_work_mode(
            "San Francisco, CA | Hybrid"
        )
        == "HYBRID"
    )

    # ---------------------------------------------------------------
    # ONSITE
    # ---------------------------------------------------------------

    assert (
        classify_work_mode(
            "On-site - San Francisco, CA"
        )
        == "ONSITE"
    )

    assert (
        classify_work_mode(
            "Onsite - New York, NY"
        )
        == "ONSITE"
    )

    assert (
        classify_work_mode(
            "In-office - London, UK"
        )
        == "ONSITE"
    )

    # ---------------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------------

    assert (
        classify_work_mode(
            "San Francisco, CA"
        )
        == "UNKNOWN"
    )

    assert (
        classify_work_mode(
            "London, UK"
        )
        == "UNKNOWN"
    )

    assert (
        classify_work_mode(
            "Tokyo, Japan"
        )
        == "UNKNOWN"
    )

    assert (
        classify_work_mode(None)
        == "UNKNOWN"
    )

    # Description is intentionally irrelevant because
    # classification is based on location only.

    print(
        "Job posting work mode backfill test passed."
    )


if __name__ == "__main__":
    main()