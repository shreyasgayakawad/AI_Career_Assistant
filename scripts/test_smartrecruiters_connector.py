"""
Test SmartRecruiters Connector

Integration test for the SmartRecruiters API connector.
"""

from app.connectors.smartrecruiters_connector import SmartRecruitersConnector


def main() -> None:
    """
    Fetch and display jobs from a SmartRecruiters board.
    """

    connector = SmartRecruitersConnector("continental")

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("SmartRecruiters Connector Test")
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
            raise RuntimeError(
                "SmartRecruiters connector returned no jobs."
            )

        if not any(job.external_job_id for job in jobs):
            raise RuntimeError(
                "No SmartRecruiters jobs contained external_job_id."
            )

        if not any(job.url for job in jobs):
            raise RuntimeError(
                "No SmartRecruiters jobs contained valid URLs."
            )

        if not any(job.location for job in jobs):
            raise RuntimeError(
                "No SmartRecruiters jobs contained location data."
            )

        # Verify pagination worked: continental has 900+ jobs
        if len(jobs) < 100:
            raise RuntimeError(
                f"Expected >100 jobs via pagination, got {len(jobs)}."
            )

        print("SmartRecruiters connector test passed.")

    finally:
        connector.close()


if __name__ == "__main__":
    main()
