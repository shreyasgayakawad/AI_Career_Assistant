"""
Job Schemas

Pydantic models for Job API responses.
"""

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    """
    Job response model.
    """

    id: int
    title: str
    company: str

    model_config = ConfigDict(
        from_attributes=True,
    )