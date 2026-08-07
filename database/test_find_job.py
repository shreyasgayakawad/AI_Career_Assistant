from database.job_service import JobService


def main():
    service = JobService()

    url = "https://example.com/job1"

    job = service.get_job_by_url(url)

    if job:
        print("✅ Job found!")
        print(f"Company : {job.company}")
        print(f"Title   : {job.title}")
        print(f"Location: {job.location}")
    else:
        print("❌ Job not found")

    service.close()


if __name__ == "__main__":
    main()