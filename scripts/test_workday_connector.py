"""
Test Workday Connector

Integration test for the Workday CXS API connector.
"""

from app.connectors.workday_connector import WorkdayConnector


def main() -> None:
    """
    Fetch and display jobs from a Workday-hosted career site.
    """

    connector = WorkdayConnector(
        wd_server="wd5",
        tenant="hp",
        site="ExternalCareerSite",
    )

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("Workday Connector Test")
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
            raise RuntimeError("Workday connector returned no jobs.")

        if not any(job.url for job in jobs):
            raise RuntimeError("No Workday jobs contained valid URLs.")

        print("Workday connector test passed.")

    finally:
        connector.close()


if __name__ == "__main__":
    main()