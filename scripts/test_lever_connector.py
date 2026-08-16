"""
Test Lever Connector

Integration test for the Lever API connector.
"""

from app.connectors.lever_connector import LeverConnector


def main() -> None:
    """
    Fetch and display jobs from a Lever board.
    """

    connector = LeverConnector("palantir")

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("Lever Connector Test")
        print("=" * 60)

        print()
        print(f"Source : {connector.source_name}")
        print(f"Jobs   : {len(jobs)}")
        print()

        for index, job in enumerate(jobs[:10], start=1):
            print(f"{index}. {job.title}")
            print(f"   Company        : {job.company}")
            print(f"   Location       : {job.location}")
            print(f"   Work Mode      : {job.work_mode}")
            print(f"   External ID    : {job.external_job_id}")
            print(f"   URL            : {job.url}")
            print()

        if not jobs:
            raise RuntimeError("Lever connector returned no jobs.")

        if not any(job.external_job_id for job in jobs):
            raise RuntimeError("No Lever jobs contained external_job_id.")

        if not any(job.url for job in jobs):
            raise RuntimeError("No Lever jobs contained valid URLs.")

        print("Lever connector test passed.")

    finally:
        connector.close()


if __name__ == "__main__":
    main()
