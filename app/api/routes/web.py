"""
Browser Routes

Provides the browser sign-in, session, career dashboard,
job-detail, application, and candidate profile pages.
"""

from html import escape

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_access_token
from app.config.settings import AUTH_COOKIE_NAME, GOOGLE_ENABLED
from app.models.job_posting import JobPosting
from app.models.user import User
from app.services.application_service import ApplicationService
from app.services.candidate_profile_service import (
    CandidateProfileService,
)
from app.services.job_matching_service import JobMatchingService
from app.services.job_search_service import JobSearchService
from app.services.portal_connection_service import (
    PortalConnectionService,
)
from app.services.resume_assistant_service import (
    COVER_LETTER_DRAFT_NOTE,
    ResumeAssistantService,
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

          <title>
            Your session | AI Career Assistant
          </title>

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

            .navigation {{
              display: flex;
              flex-wrap: wrap;
              gap: 16px;
              margin-top: 24px;
            }}
          </style>
        </head>

        <body>
          <main>
            <h1>
              Welcome, {escape(user.name)}
            </h1>

            <p>
              {escape(user.email)}
            </p>

            <section>
              <h2>LinkedIn</h2>

              <p class="status">
                {linkedin_status}
              </p>
            </section>

            <nav class="navigation">
              <a href="/dashboard">
                Open Career Dashboard
              </a>

              <a href="/dashboard/profile">
                Candidate Profile
              </a>
            </nav>
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
              <h2>
                {escape(posting.title)}
              </h2>

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

            form.search-form {{
              display: grid;
              gap: 12px;
              grid-template-columns: 1fr 1fr auto;
              margin-top: 24px;
            }}

            input {{
              border: 1px solid #d6dce5;
              border-radius: 8px;
              padding: 12px;
              box-sizing: border-box;
              width: 100%;
            }}

            button {{
              background: #1a73e8;
              border: 0;
              border-radius: 8px;
              color: white;
              cursor: pointer;
              padding: 12px 20px;
              font-weight: 700;
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
              form.search-form {{
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
                class="search-form"
                method="get"
                action="/dashboard"
              >
                <input
                  type="search"
                  name="keyword"
                  placeholder="Search jobs"
                  value="{escape(keyword or '')}"
                />

                <input
                  type="search"
                  name="company"
                  placeholder="Company"
                  value="{escape(company or '')}"
                />

                <button type="submit">
                  Search
                </button>
              </form>

              <nav class="navigation">
                <a href="/dashboard">
                  Available Jobs
                </a>

                <a href="/dashboard/profile">
                  Candidate Profile
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
    "/dashboard/profile",
    response_class=HTMLResponse,
)
def dashboard_profile_page(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """
    Render the authenticated user's candidate profile.
    """

    service = CandidateProfileService(session)

    profile = service.get_or_create_profile(
        current_user.id,
    )

    phone = escape(profile.phone or "")
    location = escape(profile.location or "")
    professional_summary = escape(
        profile.professional_summary or "",
    )
    skills = escape(profile.skills or "")
    experience = escape(profile.experience or "")
    education = escape(profile.education or "")

    skills_list = profile.skills_list or []
    skills_items: list[str] = []

    for skill in skills_list:
        skills_items.append(
            f"""
            <div style="background: #f1f3f5; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
              {escape(skill.name)}
              <form
                method="post"
                action="/dashboard/profile/skills/{skill.id}/delete"
                style="display: inline;">
                <button
                  type="submit"
                  style="background: none; border: none; color: #dc3545; cursor: pointer; font-size: 12px; margin-left: 8px;">
                  &times;
                </button>
              </form>
            </div>
            """
        )

    skills_html = "".join(skills_items)

    work_experience_list = profile.work_experiences or []
    we_items: list[str] = []

    for we in work_experience_list:
        dates = ""

        if we.start_date:
            dates += we.start_date.strftime("%Y-%m-%d")

        if we.end_date:
            if dates:
                dates += " &mdash; "
            dates += we.end_date.strftime("%Y-%m-%d")

        we_items.append(
            f"""
            <div style="background: #f1f3f5; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
              <strong>{escape(we.company_name)}</strong> &mdash; {escape(we.job_title or '')}<br/>
              {dates}<br/>
              {escape(we.description or '')}
              <form
                method="post"
                action="/dashboard/profile/work-experience/{we.id}/delete"
                style="display: inline;">
                <button
                  type="submit"
                  style="background: none; border: none; color: #dc3545; cursor: pointer; font-size: 12px; margin-left: 8px;">
                  &times;
                </button>
              </form>
            </div>
            """
        )

    work_experience_html = "".join(we_items)

    education_list = profile.education_entries or []
    edu_items: list[str] = []

    for edu in education_list:
        dates = ""

        if edu.start_date:
            dates += edu.start_date.strftime("%Y-%m-%d")

        if edu.end_date:
            if dates:
                dates += " &mdash; "
            dates += edu.end_date.strftime("%Y-%m-%d")

        edu_items.append(
            f"""
            <div style="background: #f1f3f5; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
              {escape(edu.institution)} &mdash; {escape(edu.degree)}
              {', ' + escape(edu.field_of_study) if edu.field_of_study else ''}<br/>
              {dates}
              <form
                method="post"
                action="/dashboard/profile/education/{edu.id}/delete"
                style="display: inline;">
                <button
                  type="submit"
                  style="background: none; border: none; color: #dc3545; cursor: pointer; font-size: 12px; margin-left: 8px;">
                  &times;
                </button>
              </form>
            </div>
            """
        )

    education_html = "".join(edu_items)

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport"
                content="width=device-width, initial-scale=1">

          <title>
            Candidate Profile | AI Career Assistant
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

            header,
            section {{
              background: white;
              border-radius: 16px;
              box-shadow:
                0 10px 30px rgba(23, 32, 51, .10);
              padding: 24px;
            }}

            section {{
              margin-top: 24px;
            }}

            h1,
            h2 {{
              margin-top: 0;
            }}

            .profile-form {{
              display: grid;
              gap: 18px;
            }}

            .field {{
              display: grid;
              gap: 8px;
            }}

            label {{
              font-weight: 700;
            }}

            input,
            textarea {{
              border: 1px solid #d6dce5;
              border-radius: 8px;
              box-sizing: border-box;
              font-family: inherit;
              font-size: 15px;
              padding: 12px;
              width: 100%;
            }}

            textarea {{
              min-height: 130px;
              resize: vertical;
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
              font-weight: 700;
              padding: 12px 20px;
              text-decoration: none;
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

            .profile-meta {{
              color: #596579;
              line-height: 1.5;
            }}
          </style>
        </head>

        <body>
          <main>
            <header>
              <h1>Candidate Profile</h1>

              <p class="profile-meta">
                Build the profile used by the AI Career Assistant
                to understand your career background.
              </p>

              <p class="profile-meta">
                Profile for {escape(current_user.name)}.
              </p>

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

            <section>
              <form
                class="profile-form"
                method="post"
                action="/dashboard/profile"
              >
                <div class="field">
                  <label for="phone">
                    Phone
                  </label>

                  <input
                    id="phone"
                    name="phone"
                    type="text"
                    value="{phone}"
                    maxlength="50"
                  />
                </div>

                <div class="field">
                  <label for="location">
                    Location
                  </label>

                  <input
                    id="location"
                    name="location"
                    type="text"
                    value="{location}"
                    maxlength="255"
                  />
                </div>

                <div class="field">
                  <label for="professional_summary">
                    Professional Summary
                  </label>

                  <textarea
                    id="professional_summary"
                    name="professional_summary"
                  >{professional_summary}</textarea>
                </div>

                <div class="field">
                  <label for="skills">
                    Skills
                  </label>

                  <textarea
                    id="skills"
                    name="skills"
                  >{skills}</textarea>
                </div>

                <div class="field">
                  <label for="experience">
                    Experience
                  </label>

                  <textarea
                    id="experience"
                    name="experience"
                  >{experience}</textarea>
                </div>

                <div class="field">
                  <label for="education">
                    Education
                  </label>

                  <textarea
                    id="education"
                    name="education"
                  >{education}</textarea>
                </div>

                <div>
                  <button
                    class="button"
                    type="submit"
                  >
                    Save Profile
                  </button>
                </div>
              </form>
            </section>

            <section>
              <h2>Skills</h2>

              <div class="skills-list">
                {skills_html}
              </div>

              <form
                method="post"
                action="/dashboard/profile/skills/add"
                style="margin-top: 12px;"
              >
                <input
                  type="text"
                  name="skill_name"
                  placeholder="New skill"
                  required
                  style="width: 60%; margin-right: 8px;"
                />
                <button type="submit" style="width: 30%;">
                  Add
                </button>
              </form>
            </section>

            <section>
              <h2>Work Experience</h2>

              <div class="work-experience-list">
                {work_experience_html}
              </div>

              <form
                method="post"
                action="/dashboard/profile/work-experience/add"
                style="margin-top: 12px;"
              >
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 8px;">
                  <input
                    type="text"
                    name="company_name"
                    placeholder="Company"
                    required
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="job_title"
                    placeholder="Job title"
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="start_date"
                    placeholder="Start (YYYY-MM-DD)"
                    required
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="end_date"
                    placeholder="End (YYYY-MM-DD), leave blank"
                    style="width: 100%;"
                  />
                  <button type="submit">Add</button>
                </div>
              </form>
            </section>

            <section>
              <h2>Education</h2>

              <div class="education-list">
                {education_html}
              </div>

              <form
                method="post"
                action="/dashboard/profile/education/add"
                style="margin-top: 12px;"
              >
                <div style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 8px;">
                  <input
                    type="text"
                    name="institution"
                    placeholder="Institution"
                    required
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="degree"
                    placeholder="Degree"
                    required
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="field_of_study"
                    placeholder="Field of study (optional)"
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="start_date"
                    placeholder="Start (YYYY-MM-DD)"
                    style="width: 100%;"
                  />
                  <input
                    type="text"
                    name="end_date"
                    placeholder="End (YYYY-MM-DD), leave blank"
                    style="width: 100%;"
                  />
                  <button type="submit">Add</button>
                </div>
              </form>
            </section>
          </main>
        </body>
        </html>
        """,
    )


@router.post(
    "/dashboard/profile",
)
def update_dashboard_profile(
    phone: str | None = Form(default=None),
    location: str | None = Form(default=None),
    professional_summary: str | None = Form(
        default=None,
    ),
    skills: str | None = Form(default=None),
    experience: str | None = Form(default=None),
    education: str | None = Form(default=None),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Update the authenticated user's candidate profile.
    """

    service = CandidateProfileService(session)

    service.update_profile(
        user_id=current_user.id,
        phone=phone.strip() if phone else None,
        location=location.strip() if location else None,
        professional_summary=(
            professional_summary.strip()
            if professional_summary
            else None
        ),
        skills=skills.strip() if skills else None,
        experience=experience.strip() if experience else None,
        education=education.strip() if education else None,
    )

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/skills/add",
)
def add_skill_via_dashboard(
    skill_name: str | None = Form(default=None),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Add a skill to the user's profile via the dashboard.
    """

    cleaned_name = skill_name.strip() if skill_name else None

    if cleaned_name:
        service = CandidateProfileService(session)

        try:
            service.add_skill(
                user_id=current_user.id,
                name=cleaned_name,
            )
        except ValueError:
            pass

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/skills/{skill_id}/delete",
)
def remove_skill_via_dashboard(
    skill_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Remove a skill from the user's profile via the dashboard.
    """

    service = CandidateProfileService(session)

    service.remove_skill(
        user_id=current_user.id,
        skill_id=skill_id,
    )

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/work-experience/add",
)
def add_work_experience_via_dashboard(
    company_name: str | None = Form(default=None),
    job_title: str | None = Form(default=None),
    start_date: str | None = Form(default=None),
    end_date: str | None = Form(default=None),
    description: str | None = Form(default=None),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Add work experience to the user's profile via the dashboard.
    """

    cleaned_company_name = (
        company_name.strip() if company_name else None
    )
    cleaned_start_date = (
        start_date.strip() if start_date else None
    )

    if cleaned_company_name and cleaned_start_date:
        service = CandidateProfileService(session)

        try:
            service.add_work_experience(
                user_id=current_user.id,
                company_name=cleaned_company_name,
                job_title=(
                    job_title.strip() if job_title else None
                ),
                start_date=cleaned_start_date,
                end_date=(
                    end_date.strip() if end_date else None
                ),
                description=(
                    description.strip() if description else None
                ),
            )
        except ValueError:
            pass

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/work-experience/{exp_id}/delete",
)
def remove_work_experience_via_dashboard(
    exp_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Remove work experience from the user's profile via the dashboard.
    """

    service = CandidateProfileService(session)

    service.remove_work_experience(
        user_id=current_user.id,
        experience_id=exp_id,
    )

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/education/add",
)
def add_education_via_dashboard(
    institution: str | None = Form(default=None),
    degree: str | None = Form(default=None),
    field_of_study: str | None = Form(default=None),
    start_date: str | None = Form(default=None),
    end_date: str | None = Form(default=None),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Add education to the user's profile via the dashboard.
    """

    cleaned_institution = (
        institution.strip() if institution else None
    )
    cleaned_degree = degree.strip() if degree else None

    if cleaned_institution and cleaned_degree:
        service = CandidateProfileService(session)

        try:
            service.add_education(
                user_id=current_user.id,
                institution=cleaned_institution,
                degree=cleaned_degree,
                field_of_study=(
                    field_of_study.strip()
                    if field_of_study
                    else None
                ),
                start_date=(
                    start_date.strip() if start_date else None
                ),
                end_date=(
                    end_date.strip() if end_date else None
                ),
            )
        except ValueError:
            pass

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
    )


@router.post(
    "/dashboard/profile/education/{edu_id}/delete",
)
def remove_education_via_dashboard(
    edu_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    """
    Remove education from the user's profile via the dashboard.
    """

    service = CandidateProfileService(session)

    service.remove_education(
        user_id=current_user.id,
        education_id=edu_id,
    )

    return RedirectResponse(
        url="/dashboard/profile",
        status_code=303,
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
          &#10003; You have already applied to this job.
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

    # --- Job matching integration (Phase 5) -----------------------------
    # The candidate profile is fetched via get_or_create_profile(), the
    # same lazy-creation pattern used everywhere else profile data is
    # read -- a direct session.get(CandidateProfile, current_user.id)
    # would incorrectly look up by CandidateProfile's own primary key
    # using a User id, which is a different id sequence entirely and
    # would return None for virtually every real user.
    profile_service = CandidateProfileService(session)
    candidate_profile = profile_service.get_or_create_profile(
        current_user.id,
    )

    matching_service = JobMatchingService()
    match_result = matching_service.calculate_match_score(
        candidate_profile=candidate_profile,
        job_posting=job_posting,
    )

    if match_result.overall_score is None:
        match_score_html = f"""
        <p class="match-score-empty">
          {escape(match_result.zero_skills_message or "")}
        </p>
        """
    else:
        matched_skills_html = "".join(
            f'<span class="matched-skill-pill">{escape(skill)}</span>'
            for skill in match_result.matched_skills
        )

        if not matched_skills_html:
            matched_skills_html = (
                '<span class="no-matched-skills">'
                "None of your skills were found in this posting."
                "</span>"
            )

        match_score_html = f"""
        <div class="match-score">
          <p class="match-score-value">
            Match score: {match_result.overall_score:.0f}%
          </p>
          <div class="matched-skills">
            {matched_skills_html}
          </div>
        </div>
        """
    # ----------------------------------------------------------------------

    # --- Cover-letter draft integration (Phase 7) ------------------------
    # Reuses the same candidate_profile fetched above via
    # get_or_create_profile(). The draft is a fixed template filled
    # with real profile data -- no AI text generation anywhere. All
    # candidate-controlled text is escaped before it enters the HTML.
    resume_assistant_service = ResumeAssistantService()

    skill_emphasis = resume_assistant_service.get_skill_emphasis(
        candidate_profile=candidate_profile,
        job_posting=job_posting,
    )

    cover_letter_draft = (
        resume_assistant_service.generate_cover_letter_draft(
            candidate_name=current_user.name,
            candidate_profile=candidate_profile,
            job_posting=job_posting,
            company_name=job.company.name,
        )
    )

    skill_emphasis_pills_html = "".join(
        f'<span class="matched-skill-pill">{escape(skill)}</span>'
        for skill in skill_emphasis
    )

    if not skill_emphasis_pills_html:
        skill_emphasis_pills_html = (
            '<span class="no-matched-skills">'
            "None of your tracked skills were found in this posting."
            "</span>"
        )

    cover_letter_html = f"""
    <section class="cover-letter">
      <h2>Cover Letter Draft</h2>

      <p class="draft-note">
        {escape(COVER_LETTER_DRAFT_NOTE)}
      </p>

      <textarea
        class="draft-textarea"
        rows="14"
      >{escape(cover_letter_draft)}</textarea>

      <p class="skill-emphasis-label">
        Your skills found in this posting:
      </p>

      <div class="matched-skills">
        {skill_emphasis_pills_html}
      </div>
    </section>
    """
    # ----------------------------------------------------------------------

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

            .actions form {{
              margin: 0;
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

            .match-score {{
              background: #eef6ff;
              border-radius: 12px;
              margin-bottom: 24px;
              padding: 16px 20px;
            }}

            .match-score-value {{
              color: #1a73e8;
              font-size: 18px;
              font-weight: 700;
              margin: 0 0 10px;
            }}

            .matched-skills {{
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
            }}

            .matched-skill-pill {{
              background: #1a73e8;
              border-radius: 999px;
              color: white;
              font-size: 13px;
              padding: 4px 12px;
            }}

            .no-matched-skills {{
              color: #596579;
              font-size: 13px;
            }}

            .match-score-empty {{
              background: #f1f3f5;
              border-radius: 12px;
              color: #596579;
              margin-bottom: 24px;
              padding: 16px 20px;
            }}

            .cover-letter {{
              background: #f6f8fb;
              border-radius: 12px;
              margin-bottom: 24px;
              padding: 16px 20px;
            }}

            .cover-letter h2 {{
              font-size: 20px;
              margin: 0 0 10px;
            }}

            .draft-note {{
              color: #596579;
              font-size: 13px;
              margin: 0 0 12px;
            }}

            .draft-textarea {{
              border: 1px solid #d5dbe3;
              border-radius: 8px;
              box-sizing: border-box;
              font-family: inherit;
              font-size: 14px;
              line-height: 1.5;
              padding: 12px;
              width: 100%;
            }}

            .skill-emphasis-label {{
              color: #172033;
              font-weight: 700;
              margin: 14px 0 0;
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

              {match_score_html}

              {cover_letter_html}

              <section>
                <h2>Job Description</h2>

                <div class="description">
                  {description}
                </div>
              </section>

              <div class="actions">
                
                  class="button"
                  href="{posting_url}"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open Job Posting
                </a>

                {application_control}

                
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
                · Status: {escape(application.status)}
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

                <a href="/dashboard/profile">
                  Candidate Profile
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