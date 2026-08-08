"""
AI Career Assistant API

FastAPI application entry point.
"""

from fastapi import FastAPI

from app.api.routes.applications import router as applications_router
from app.api.routes.auth import router as auth_router
from app.api.routes.job_postings import router as job_postings_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.linkedin_oauth import (
    router as linkedin_oauth_router,
)
from app.api.routes.portal_connections import (
    router as portal_connections_router,
)


app = FastAPI(
    title="AI Career Assistant",
    version="1.0.0",
)


app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(job_postings_router)
app.include_router(auth_router)
app.include_router(portal_connections_router)
app.include_router(linkedin_oauth_router)


@app.get("/")
def root() -> dict[str, str]:
    """
    Health check endpoint.
    """

    return {
        "message": "AI Career Assistant API is running",
    }