from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from database.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    company = Column(String)

    title = Column(String)

    location = Column(String)

    description = Column(String)

    url = Column(String, unique=True)

    score = Column(Integer)

    status = Column(String)

    created_at = Column(DateTime, server_default=func.now())