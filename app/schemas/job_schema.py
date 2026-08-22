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


class MatchResultResponse(BaseModel):
    """
    Match result returned when computing a candidate-vs-job match score.

    overall_score is None when the candidate has no skills on their
    profile yet -- distinct from 0.0, which would otherwise look like
    a confirmed zero-percent match. Check zero_skills_message when
    overall_score is None.
    """

    overall_score: float | None
    matched_skills: list[str]
    unmatched_skills: list[str]
    location_match: bool | None
    zero_skills_message: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )