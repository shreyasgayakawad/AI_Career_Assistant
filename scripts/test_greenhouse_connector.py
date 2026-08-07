"""
Test Greenhouse Connector

Integration test for the Greenhouse API connector.
"""

from app.connectors.greenhouse_connector import GreenhouseConnector


def main() -> None:
    """
    Fetch and display jobs from a Greenhouse board.
    """

    connector = GreenhouseConnector("anthropic")

    try:
        jobs = connector.fetch_jobs()

        print("=" * 60)
        print("Greenhouse Connector Test")
        print("=" * 60)

        print(f"\nSource : {connector.source_name}")
        print(f"Jobs   : {len(jobs)}\n")

        for index, job in enumerate(jobs[:10], start=1):
            print(f"{index}. {job.title}")
            print(f"   Company : {job.company}")
            print(f"   Location: {job.location}")
            print(f"   URL     : {job.url}")
            print()

    finally:
        connector.close()


if __name__ == "__main__":
    main()