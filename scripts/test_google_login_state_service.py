"""
Test Google Login State Service

Verifies state values are unique, expire, and can only be used once.
"""

from datetime import datetime, timedelta, timezone

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.google_login_state import GoogleLoginState
from app.services.google_login_state_service import (
    GoogleLoginStateService,
)


def main() -> None:
    """
    Test Google login state creation and consumption.
    """

    session = SessionLocal()
    state_values: list[str] = []

    try:
        service = GoogleLoginStateService(session)

        print("=" * 50)
        print("Google Login State Service Test")
        print("=" * 50)

        created_state = service.create_state()
        state_values.append(created_state.state)

        if not created_state.state:
            raise RuntimeError("Google login state was not created.")

        if created_state.expires_at <= datetime.now(
            timezone.utc,
        ).replace(tzinfo=None):
            raise RuntimeError("Google login state was not given an expiry.")

        print("State Creation            : Passed")

        consumed_state = service.consume_state(
            created_state.state,
        )

        if consumed_state.state != created_state.state:
            raise RuntimeError("Google login state was consumed incorrectly.")

        print("State Consumption         : Passed")

        try:
            service.consume_state(created_state.state)

            raise RuntimeError("Google login state was reused.")

        except ValueError as exc:
            if str(exc) != "Invalid Google login state.":
                raise RuntimeError(
                    "Unexpected reused-state error: "
                    f"{exc}"
                ) from exc

        print("State Replay Rejected     : Passed")

        expired_state = service.create_state()
        state_values.append(expired_state.state)
        expired_state.expires_at = (
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ).replace(tzinfo=None)
        session.commit()

        try:
            service.consume_state(expired_state.state)

            raise RuntimeError("Expired Google login state was accepted.")

        except ValueError as exc:
            if str(exc) != "Google login state has expired.":
                raise RuntimeError(
                    "Unexpected expired-state error: "
                    f"{exc}"
                ) from exc

        print("Expired State Rejected    : Passed")

        print()
        print("Google login state service test passed.")

    finally:
        session.query(GoogleLoginState).filter(
            GoogleLoginState.state.in_(state_values),
        ).delete(synchronize_session=False)
        session.commit()
        session.close()


if __name__ == "__main__":
    main()
