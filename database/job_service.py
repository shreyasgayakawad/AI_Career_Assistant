from database.database import SessionLocal
from models.job import Job


class JobService:
    def __init__(self):
        self.db = SessionLocal()

    def add_job(self, job: Job):
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_all_jobs(self):
        return self.db.query(Job).all()

    def get_job_by_url(self, url: str):
    	return self.db.query(Job).filter(Job.url == url).first()

    def close(self):
        self.db.close()