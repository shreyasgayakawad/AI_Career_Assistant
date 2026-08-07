from database.database import SessionLocal
from models.job import Job


def read_jobs():
    db = SessionLocal()

    jobs = db.query(Job).all()

    if not jobs:
        print("No jobs found.")
    else:
        print(f"Found {len(jobs)} job(s):\n")

        for job in jobs:
            print(f"ID: {job.id}")
            print(f"Company: {job.company}")
            print(f"Title: {job.title}")
            print(f"Location: {job.location}")
            print(f"Score: {job.score}")
            print(f"Status: {job.status}")
            print("-" * 40)

    db.close()


if __name__ == "__main__":
    read_jobs()