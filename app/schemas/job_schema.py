"""
Job Schemas

Pydantic models for Job API requests and responses.
"""

from pydantic import BaseModel, ConfigDict


class JobSummaryResponse(BaseModel):
    """
    Job posting summary returned in job listings.
    """

    id: int
    job_id: int
    title: str
    company: str
    location: str | None
    work_mode: str
    posting_url: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class JobDetailResponse(BaseModel):
    """
    Detailed job posting information.
    """

    id: int
    job_id: int
    title: str
    company: str
    location: str | None
    work_mode: str
    posting_url: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )