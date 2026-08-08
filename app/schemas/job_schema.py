"""
Job Schemas

Pydantic models for Job API requests and responses.
"""

from pydantic import BaseModel, ConfigDict


class JobSummaryResponse(BaseModel):
    """
    Job summary returned in job listings.
    """

    id: int
    title: str
    company: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class JobDetailResponse(BaseModel):
    """
    Detailed job information.
    """

    id: int
    title: str
    company: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )