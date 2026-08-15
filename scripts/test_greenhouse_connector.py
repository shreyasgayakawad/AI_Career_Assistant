"""
Test Greenhouse Connector

Integration test for the Greenhouse API connector.
"""

from app.connectors.greenhouse_connector import (
    GreenhouseConnector,
)


def main() -> None:
    """
    Fetch and display jobs from a Greenhouse board.
    """

    connector = GreenhouseConnector(
        "anthropic",
    )

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("Greenhouse Connector Test")
        print("=" * 60)

        print()
        print(
            f"Source : {connector.source_name}"
        )
        print(
            f"Jobs   : {len(jobs)}"
        )

        print()

        for index, job in enumerate(
            jobs[:10],
            start=1,
        ):
            print(
                f"{index}. {job.title}"
            )
            print(
                f"   Company   : {job.company}"
            )
            print(
                f"   Location  : {job.location}"
            )
            print(
                f"   Work Mode : {job.work_mode}"
            )
            print(
                f"   URL       : {job.url}"
            )
            print()

        if not jobs:
            raise RuntimeError(
                "Greenhouse connector returned no jobs."
            )

        if not any(
            job.work_mode is not None
            for job in jobs
        ):
            raise RuntimeError(
                "No Greenhouse jobs contained "
                "Location Type metadata."
            )

        print(
            "Greenhouse connector test passed."
        )

    finally:
        connector.close()


if __name__ == "__main__":
    main()