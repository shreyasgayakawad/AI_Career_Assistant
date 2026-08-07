from database.database import Base, engine
from models.job import Job


def init_database():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_database()