from database.job_service import JobService


def main():
    service = JobService()

    jobs = service.get_all_jobs()

    print("=" * 50)
    print("AI Job Bot")
    print("=" * 50)

    print(f"\nFound {len(jobs)} jobs\n")

    for job in jobs:
        print(f"{job.company} | {job.title} | {job.location}")

    service.close()


if __name__ == "__main__":
    main()