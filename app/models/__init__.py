"""
Application Models

Import all SQLAlchemy models so they are registered with the ORM.
"""

from app.models.application import Application
from app.models.company import Company
from app.models.job import Job
from app.models.job_posting import JobPosting
from app.models.oauth_state import OAuthState
from app.models.portal_connection import PortalConnection
from app.models.source import Source
from app.models.user import User


__all__ = [
    "Application",
    "Company",
    "Job",
    "JobPosting",
    "OAuthState",
    "PortalConnection",
    "Source",
    "User",
]