"""
Test Ashby Connector

Integration test for the Ashby API connector.
"""

from app.connectors.ashby_connector import AshbyConnector


def main() -> None:
    """
    Fetch and display jobs from an Ashby board.
    """

    connector = AshbyConnector("linear")

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("Ashby Connector Test")
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
            print(f"   Posted Date    : {job.posted_date}")
            print(f"   URL            : {job.url}")
            print()

        if not jobs:
            raise RuntimeError("Ashby connector returned no jobs.")

        if not any(job.external_job_id for job in jobs):
            raise RuntimeError("No Ashby jobs contained external_job_id.")

        if not any(job.url for job in jobs):
            raise RuntimeError("No Ashby jobs contained valid URLs.")

        if not any(job.work_mode for job in jobs):
            raise RuntimeError("No Ashby jobs contained work_mode.")

        print("Ashby connector test passed.")

    finally:
        connector.close()


if __name__ == "__main__":
    main()
