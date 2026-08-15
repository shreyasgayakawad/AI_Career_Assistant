"""
Test Greenhouse Work Mode Extraction

Verifies that Greenhouse Location Type metadata is extracted and
normalized into the application's supported work-mode values.
"""

from app.connectors.greenhouse_connector import GreenhouseConnector
from app.services.job_normalization_service import (
    JobNormalizationService,
)


EXPECTED_NORMALIZED_MODES = {
    "REMOTE",
    "HYBRID",
    "ONSITE",
    "UNKNOWN",
}


def main() -> None:
    """
    Verify Greenhouse work-mode extraction and normalization.
    """

    connector = GreenhouseConnector("anthropic")
    normalization_service = JobNormalizationService()

    try:
        jobs = connector.fetch_jobs()

        if not jobs:
            raise RuntimeError(
                "Greenhouse returned no jobs."
            )

        raw_work_modes = {
            job.work_mode
            for job in jobs
            if job.work_mode is not None
        }

        normalized_modes = {
            normalization_service._normalize_work_mode(
                value,
            )
            for value in raw_work_modes
        }

        print("=" * 60)
        print("Greenhouse Work Mode Test")
        print("=" * 60)
        print()
        print(f"Jobs fetched      : {len(jobs)}")
        print(
            f"Raw work modes    : "
            f"{sorted(raw_work_modes)}"
        )
        print(
            f"Normalized modes  : "
            f"{sorted(normalized_modes)}"
        )

        if not raw_work_modes:
            raise RuntimeError(
                "No Greenhouse work-mode metadata was found."
            )

        invalid_modes = (
            normalized_modes - EXPECTED_NORMALIZED_MODES
        )

        if invalid_modes:
            raise RuntimeError(
                "Invalid normalized work modes: "
                f"{sorted(invalid_modes)}"
            )

        if "HYBRID" not in normalized_modes:
            raise RuntimeError(
                "HYBRID work mode was not detected."
            )

        if "ONSITE" not in normalized_modes:
            raise RuntimeError(
                "ONSITE work mode was not detected."
            )

        if "REMOTE" not in normalized_modes:
            raise RuntimeError(
                "REMOTE work mode was not detected."
            )

        print()
        print("Greenhouse work mode test passed.")

    finally:
        connector.close()


if __name__ == "__main__":
    main()