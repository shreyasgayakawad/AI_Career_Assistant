from database.database import SessionLocal
from models.job import Job


def insert_test_job():
    db = SessionLocal()

    job = Job(
        company="Blue Yonder",
        title="Application Support Engineer",
        location="Bangalore",
        description="Test Job",
        url="https://example.com/job1",
        score=95,
        status="NEW"
    )

    db.add(job)
    db.commit()

    print("✅ Test job inserted successfully!")

    db.close()


if __name__ == "__main__":
    insert_test_job()