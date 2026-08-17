"""
Application Models

Import all SQLAlchemy models so they are registered with the ORM.
"""

from app.models.application import Application
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_education import CandidateEducation
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_work_experience import CandidateWorkExperience
from app.models.company import Company
from app.models.google_login_state import GoogleLoginState
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.oauth_state import OAuthState
from app.models.portal_connection import PortalConnection
from app.models.source import Source
from app.models.user import User

__all__ = [
    "Application",
    "CandidateProfile",
    "CandidateEducation",
    "CandidateSkill",
    "CandidateWorkExperience",
    "Company",
    "GoogleLoginState",
    "Job",
    "JobPosting",
    "OAuthState",
    "PortalConnection",
    "Source",
    "User",
]