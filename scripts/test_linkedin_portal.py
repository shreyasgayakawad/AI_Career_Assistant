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
    # Feature flag handling.
    # ---------------------------------------------------------

    if not LINKEDIN_ENABLED:
        print(
            "LinkedIn Feature Flag : Disabled (Testing Disabled Handling)"
        )

        try:
            portal.connect()
            raise RuntimeError(
                "LinkedIn connection succeeded while disabled."
            )
        except RuntimeError as exc:
            expected_message = "LinkedIn integration is disabled."
            if str(exc) != expected_message:
                raise RuntimeError(
                    f"Unexpected LinkedIn connection error: {exc}"
                ) from exc

        print(
            "Disabled Connection Rejected : Passed"
        )

        try:
            portal.disconnect()
            raise RuntimeError(
                "LinkedIn disconnection succeeded while disabled."
            )
        except RuntimeError as exc:
            expected_message = "LinkedIn integration is disabled."
            if str(exc) != expected_message:
                raise RuntimeError(
                    f"Unexpected LinkedIn disconnection error: {exc}"
                ) from exc

        print(
            "Disabled Disconnection Rejected : Passed"
        )
    else:
        print(
            "LinkedIn Feature Flag : Enabled (Testing Enabled Handling)"
        )

        try:
            portal.connect()
            raise RuntimeError(
                "LinkedIn connection should raise NotImplementedError when enabled."
            )
        except NotImplementedError:
            pass

        print(
            "Enabled Connection NotImplemented : Passed"
        )

        try:
            portal.disconnect()
            raise RuntimeError(
                "LinkedIn disconnection should raise NotImplementedError when enabled."
            )
        except NotImplementedError:
            pass

        print(
            "Enabled Disconnection NotImplemented : Passed"
        )

    print()
    print(
        "LinkedIn portal adapter test passed."
    )


if __name__ == "__main__":
    main()