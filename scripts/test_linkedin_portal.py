"""
LinkedIn Portal Adapter Test

Tests the LinkedIn portal adapter contract.
"""

from app.config.settings import LINKEDIN_ENABLED
from app.connectors.base_portal import BasePortal
from app.connectors.linkedin_portal import LinkedInPortal


def main() -> None:
    """
    Test LinkedInPortal behavior.
    """

    portal = LinkedInPortal()

    print()
    print("# LinkedIn Portal Adapter Test")
    print()

    # ---------------------------------------------------------
    # Platform name.
    # ---------------------------------------------------------

    if portal.platform_name != "LinkedIn":
        raise RuntimeError(
            "LinkedIn portal returned an incorrect platform name."
        )

    print(
        "Platform Name : Passed"
    )

    # ---------------------------------------------------------
    # Base interface.
    # ---------------------------------------------------------

    if not isinstance(portal, BasePortal):
        raise RuntimeError(
            "LinkedInPortal does not implement BasePortal."
        )

    print(
        "Base Portal Contract : Passed"
    )

    # ---------------------------------------------------------
    # Feature flag.
    # ---------------------------------------------------------

    if LINKEDIN_ENABLED:
        raise RuntimeError(
            "LinkedIn should be disabled during this test."
        )

    print(
        "LinkedIn Feature Flag : Passed"
    )

    # ---------------------------------------------------------
    # Connect while disabled.
    # ---------------------------------------------------------

    try:
        portal.connect()

        raise RuntimeError(
            "LinkedIn connection succeeded while disabled."
        )

    except RuntimeError as exc:
        expected_message = (
            "LinkedIn integration is disabled."
        )

        if str(exc) != expected_message:
            raise RuntimeError(
                "Unexpected LinkedIn connection error: "
                f"{exc}"
            ) from exc

    print(
        "Disabled Connection Rejected : Passed"
    )

    # ---------------------------------------------------------
    # Disconnect while disabled.
    # ---------------------------------------------------------

    try:
        portal.disconnect()

        raise RuntimeError(
            "LinkedIn disconnection succeeded while disabled."
        )

    except RuntimeError as exc:
        expected_message = (
            "LinkedIn integration is disabled."
        )

        if str(exc) != expected_message:
            raise RuntimeError(
                "Unexpected LinkedIn disconnection error: "
                f"{exc}"
            ) from exc

    print(
        "Disabled Disconnection Rejected : Passed"
    )

    print()
    print(
        "LinkedIn portal adapter test passed."
    )


if __name__ == "__main__":
    main()