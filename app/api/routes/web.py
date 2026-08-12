"""
Browser Routes

Provides the browser sign-in, session, career dashboard,
job-detail, and application pages.
"""

from html import escape

from fastapi import APIRouter, Cookie, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_access_token
from app.config.settings import AUTH_COOKIE_NAME, GOOGLE_ENABLED
from app.models.job_posting import JobPosting
from app.models.user import User
from app.services.application_service import ApplicationService
from app.services.job_search_service import JobSearchService
from app.services.portal_connection_service import (
    PortalConnectionService,
)

router = APIRouter(tags=["Browser"])


@router.get("/", response_class=HTMLResponse)
def sign_in_page() -> HTMLResponse:
    """
    Render the browser sign-in page.
    """

    if GOOGLE_ENABLED:
        google_control = (
            '<a class="google-button" href="/auth/google/authorize">'
            "Continue with Google</a>"
        )
        status_message = "Use your Google account to continue."
    else:
        google_control = (
            '<button class="google-button" disabled>'
            "Continue with Google</button>"
        )
        status_message = "Google sign-in is being configured."

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">
          <title>AI Career Assistant</title>

          <style>
            body {{
              font-family: Arial, sans-serif;
              background: #f7f8fc;
              color: #172033;
              display: grid;
              min-height: 100vh;
              margin: 0;
              place-items: center;
            }}

            main {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .12);
              max-width: 420px;
              padding: 42px;
              text-align: center;
            }}

            h1 {{
              margin: 0 0 12px;
            }}

            p {{
              color: #596579;
              line-height: 1.5;
            }}

            .google-button {{
              background: #1a73e8;
              border: 0;
              border-radius: 8px;
              color: white;
              display: block;
              font-size: 16px;
              margin-top: 28px;
              padding: 14px 20px;
              text-decoration: none;
              width: 100%;
              box-sizing: border-box;
            }}

            button:disabled {{
              background: #9aa8ba;
              cursor: not-allowed;
            }}
          </style>
        </head>

        <body>
          <main>
            <h1>AI Career Assistant</h1>

            <p>
              Sign in to view your connected job platforms.
            </p>

            {google_control}

            <p aria-live="polite">
              {status_message}
            </p>
          </main>
        </body>
        </html>
        """,
    )


@router.get(
    "/session",
    response_class=HTMLResponse,
    response_model=None,
)
def session_page(
    browser_access_token: str | None = Cookie(
        default=None,
        alias=AUTH_COOKIE_NAME,
    ),
    session: Session = Depends(get_db),
) -> HTMLResponse | RedirectResponse:
    """
    Render the signed-in user's connected-platform summary.
    """

    if not browser_access_token:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    try:
        user_id = decode_access_token(
            browser_access_token,
        )
    except ValueError:
        response = RedirectResponse(
            url="/",
            status_code=303,
        )
        response.delete_cookie(AUTH_COOKIE_NAME)
        return response

    user = session.get(
        User,
        user_id,
    )

    if user is None:
        response = RedirectResponse(
            url="/",
            status_code=303,
        )
        response.delete_cookie(AUTH_COOKIE_NAME)
        return response

    service = PortalConnectionService(session)

    linkedin = service.get_connection(
        user.id,
        "LinkedIn",
    )

    linkedin_connected = bool(
        linkedin
        and linkedin.status == "ACTIVE"
        and linkedin.enabled
        and linkedin.credential_reference
    )

    linkedin_status = (
        "Connected"
        if linkedin_connected
        else "Not connected"
    )

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">
          <title>Your session | AI Career Assistant</title>

          <style>
            body {{
              font-family: Arial, sans-serif;
              background: #f7f8fc;
              color: #172033;
              margin: 0;
            }}

            main {{
              margin: 72px auto;
              max-width: 680px;
              padding: 32px;
            }}

            section {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .10);
              margin-top: 24px;
              padding: 24px;
            }}

            .status {{
              color: #147a43;
              font-weight: 700;
            }}

            a {{
              color: #1a73e8;
              font-weight: 700;
            }}
          </style>
        </head>

        <body>
          <main>
            <h1>Welcome, {escape(user.name)}</h1>

            <p>
              {escape(user.email)}
            </p>

            <section>
              <h2>LinkedIn</h2>

              <p class="status">
                {linkedin_status}
              </p>
            </section>

            <p>
              <a href="/dashboard">
                Open Career Dashboard
              </a>
            </p>
          </main>
        </body>
        </html>
        """,
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard_page(
    keyword: str | None = None,
    company: str | None = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """
    Render the authenticated career dashboard.
    """

    service = JobSearchService(session)

    postings = service.search_available_postings(
        keyword=keyword,
        company_name=company,
    )

    job_cards: list[str] = []

    for posting in postings:
        job_cards.append(
            f"""
            <article class="job-card">
              <h2>{escape(posting.title)}</h2>

              <p>
                <strong>
                  {escape(posting.job.company.name)}
                </strong>
                ·
                {escape(
                    posting.location
                    or "Location not specified"
                )}
              </p>

              <a href="/dashboard/jobs/{posting.id}">
                View Details
              </a>
            </article>
            """
        )

    jobs_html = "".join(job_cards)

    if not jobs_html:
        jobs_html = """
        <p class="empty">
          No available jobs match your search.
        </p>
        """

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">

          <title>
            Dashboard | AI Career Assistant
          </title>

          <style>
            body {{
              font-family: Arial, sans-serif;
              background: #f7f8fc;
              color: #172033;
              margin: 0;
            }}

            main {{
              margin: 48px auto;
              max-width: 900px;
              padding: 24px;
            }}

            header {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .10);
              padding: 24px;
            }}

            h1 {{
              margin-top: 0;
            }}

            form {{
              display: grid;
              gap: 12px;
              grid-template-columns:
                1fr 1fr auto;
              margin-top: 24px;
            }}

            input {{
              border: 1px solid #d6dce5;
              border-radius: 8px;
              padding: 12px;
            }}

            button {{
              background: #1a73e8;
              border: 0;
              border-radius: 8px;
              color: white;
              cursor: pointer;
              padding: 12px 20px;
            }}

            .jobs {{
              display: grid;
              gap: 16px;
              margin-top: 24px;
            }}

            .job-card {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .08);
              padding: 24px;
            }}

            .job-card h2 {{
              margin-top: 0;
            }}

            .job-card a {{
              color: #1a73e8;
              font-weight: 700;
              text-decoration: none;
            }}

            .empty {{
              background: white;
              border-radius: 16px;
              padding: 24px;
            }}

            .navigation {{
              display: flex;
              flex-wrap: wrap;
              gap: 16px;
              margin-top: 20px;
            }}

            .navigation a {{
              color: #1a73e8;
              font-weight: 700;
              text-decoration: none;
            }}

            @media (max-width: 700px) {{
              form {{
                grid-template-columns: 1fr;
              }}
            }}
          </style>
        </head>

        <body>
          <main>
            <header>
              <h1>AI Career Assistant</h1>

              <p>
                Welcome, {escape(current_user.name)}.
              </p>

              <form
                method="get"
                action="/dashboard"
              >
                <input
                  type="search"
                  name="keyword"
                  placeholder="Search jobs"
                  value="{escape(keyword or "")}"
                />

                <input
                  type="search"
                  name="company"
                  placeholder="Company"
                  value="{escape(company or "")}"
                />

                <button type="submit">
                  Search
                </button>
              </form>

              <nav class="navigation">
                <a href="/dashboard">
                  Available Jobs
                </a>

                <a href="/dashboard/applications">
                  My Applications
                </a>

                <a href="/session">
                  Connection Status
                </a>
              </nav>
            </header>

            <section class="jobs">
              {jobs_html}
            </section>
          </main>
        </body>
        </html>
        """,
    )


@router.get(
    "/dashboard/jobs/{job_posting_id}",
    response_class=HTMLResponse,
)
def dashboard_job_detail_page(
    job_posting_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """
    Render the details of an available job posting.
    """

    job_posting = session.get(
        JobPosting,
        job_posting_id,
    )

    if job_posting is None:
        return HTMLResponse(
            content="""
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>Job Not Found</title>
            </head>

            <body>
              <main>
                <h1>Job Not Found</h1>

                <p>
                  The requested job posting does not exist.
                </p>

                <p>
                  <a href="/dashboard">
                    Back to Dashboard
                  </a>
                </p>
              </main>
            </body>
            </html>
            """,
            status_code=404,
        )

    if job_posting.status != "ACTIVE":
        return HTMLResponse(
            content="""
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>Job Not Available</title>
            </head>

            <body>
              <main>
                <h1>Job Not Available</h1>

                <p>
                  This job posting is no longer active.
                </p>

                <p>
                  <a href="/dashboard">
                    Back to Dashboard
                  </a>
                </p>
              </main>
            </body>
            </html>
            """,
            status_code=404,
        )

    job_search_service = JobSearchService(session)

    job = job_search_service.get_job(
        job_posting.job_id,
    )

    if job is None:
        return HTMLResponse(
            content="""
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>Job Not Found</title>
            </head>

            <body>
              <main>
                <h1>Job Not Found</h1>

                <p>
                  The associated job could not be found.
                </p>

                <p>
                  <a href="/dashboard">
                    Back to Dashboard
                  </a>
                </p>
              </main>
            </body>
            </html>
            """,
            status_code=404,
        )

    application_service = ApplicationService(session)

    already_applied = application_service.has_applied(
        user_id=current_user.id,
        job_posting_id=job_posting.id,
    )

    if already_applied:
        application_control = """
        <p class="applied">
          ✓ You have already applied to this job.
        </p>
        """
    else:
        application_control = f"""
        <form
          method="post"
          action="/dashboard/jobs/{job_posting.id}/apply"
        >
          <button
            class="button apply-button"
            type="submit"
          >
            Mark as Applied
          </button>
        </form>
        """

    description = (
        escape(job_posting.description)
        if job_posting.description
        else "No description is available."
    )

    location = escape(
        job_posting.location
        or "Location not specified"
    )

    company_name = escape(
        job.company.name
    )

    posting_url = escape(
        job_posting.posting_url,
        quote=True,
    )

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">

          <title>
            {escape(job_posting.title)}
            | AI Career Assistant
          </title>

          <style>
            body {{
              font-family: Arial, sans-serif;
              background: #f7f8fc;
              color: #172033;
              margin: 0;
            }}

            main {{
              margin: 48px auto;
              max-width: 900px;
              padding: 24px;
            }}

            article {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .10);
              padding: 32px;
            }}

            h1 {{
              margin-top: 0;
            }}

            .metadata {{
              color: #596579;
              margin-bottom: 28px;
            }}

            .description {{
              line-height: 1.7;
              white-space: pre-wrap;
            }}

            .actions {{
              align-items: center;
              display: flex;
              flex-wrap: wrap;
              gap: 12px;
              margin-top: 32px;
            }}

            .button {{
              background: #1a73e8;
              border: 0;
              border-radius: 8px;
              color: white;
              cursor: pointer;
              display: inline-block;
              font-family: inherit;
              font-size: 15px;
              padding: 12px 20px;
              text-decoration: none;
              font-weight: 700;
            }}

            .secondary {{
              background: #eef2f7;
              color: #172033;
            }}

            .applied {{
              color: #147a43;
              font-weight: 700;
              margin: 0;
            }}
          </style>
        </head>

        <body>
          <main>
            <article>
              <h1>
                {escape(job_posting.title)}
              </h1>

              <p class="metadata">
                <strong>{company_name}</strong>
                · {location}
              </p>

              <section>
                <h2>Job Description</h2>

                <div class="description">
                  {description}
                </div>
              </section>

              <div class="actions">
                <a
                  class="button"
                  href="{posting_url}"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open Job Posting
                </a>

                {application_control}

                <a
                  class="button secondary"
                  href="/dashboard"
                >
                  Back to Jobs
                </a>
              </div>
            </article>
          </main>
        </body>
        </html>
        """,
    )


@router.post(
    "/dashboard/jobs/{job_posting_id}/apply",
)
def mark_dashboard_job_as_applied(
    job_posting_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Mark a dashboard job posting as applied.
    """

    job_posting = session.get(
        JobPosting,
        job_posting_id,
    )

    if job_posting is None:
        return RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

    service = ApplicationService(session)

    try:
        service.mark_as_applied(
            user_id=current_user.id,
            job_posting_id=job_posting_id,
        )
    except ValueError:
        pass

    return RedirectResponse(
        url=f"/dashboard/jobs/{job_posting_id}",
        status_code=303,
    )


@router.get(
    "/dashboard/applications",
    response_class=HTMLResponse,
)
def dashboard_applications_page(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """
    Render the authenticated user's applications.
    """

    service = ApplicationService(session)

    applications = service.get_all_applications(
        user_id=current_user.id,
    )

    application_cards: list[str] = []

    for application in applications:
        job_posting = session.get(
            JobPosting,
            application.job_posting_id,
        )

        if job_posting is None:
            continue

        company_name = (
            job_posting.job.company.name
            if job_posting.job
            and job_posting.job.company
            else "Unknown company"
        )

        application_cards.append(
            f"""
            <article class="application-card">
              <h2>
                {escape(job_posting.title)}
              </h2>

              <p>
                <strong>
                  {escape(company_name)}
                </strong>
                ·
                {escape(
                    job_posting.location
                    or "Location not specified"
                )}
              </p>

              <p class="applied-date">
                Applied:
                {escape(
                    application.applied_at.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )}
              </p>

              <a href="/dashboard/jobs/{job_posting.id}">
                View Job
              </a>
            </article>
            """
        )

    applications_html = "".join(
        application_cards,
    )

    if not applications_html:
        applications_html = """
        <p class="empty">
          You have not marked any jobs as applied.
        </p>
        """

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">

          <title>
            My Applications | AI Career Assistant
          </title>

          <style>
            body {{
              font-family: Arial, sans-serif;
              background: #f7f8fc;
              color: #172033;
              margin: 0;
            }}

            main {{
              margin: 48px auto;
              max-width: 900px;
              padding: 24px;
            }}

            header {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .10);
              padding: 24px;
            }}

            .applications {{
              display: grid;
              gap: 16px;
              margin-top: 24px;
            }}

            .application-card {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .08);
              padding: 24px;
            }}

            .application-card h2 {{
              margin-top: 0;
            }}

            .application-card a {{
              color: #1a73e8;
              font-weight: 700;
              text-decoration: none;
            }}

            .applied-date {{
              color: #596579;
            }}

            .empty {{
              background: white;
              border-radius: 16px;
              padding: 24px;
            }}

            nav {{
              display: flex;
              flex-wrap: wrap;
              gap: 16px;
              margin-top: 20px;
            }}

            nav a {{
              color: #1a73e8;
              font-weight: 700;
              text-decoration: none;
            }}
          </style>
        </head>

        <body>
          <main>
            <header>
              <h1>My Applications</h1>

              <p>
                Applications for
                {escape(current_user.name)}.
              </p>

              <nav>
                <a href="/dashboard">
                  Available Jobs
                </a>

                <a href="/session">
                  Connection Status
                </a>
              </nav>
            </header>

            <section class="applications">
              {applications_html}
            </section>
          </main>
        </body>
        </html>
        """,
    )