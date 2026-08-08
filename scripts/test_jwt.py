"""
JWT Utility Test

Tests access-token creation and decoding.
"""

from app.auth.jwt import (
    create_access_token,
    decode_access_token,
)


def main() -> None:
    """
    Test JWT creation and decoding.
    """

    user_id = 123

    token = create_access_token(
        user_id,
    )

    print("# JWT Test")
    print()
    print(f"Token created : {bool(token)}")

    if not token:
        raise RuntimeError(
            "JWT token was not created."
        )

    decoded_user_id = decode_access_token(
        token,
    )

    print(
        f"Decoded User ID : {decoded_user_id}"
    )

    if decoded_user_id != user_id:
        raise RuntimeError(
            "Decoded user ID does not match."
        )

    print()
    print("Token Creation : Passed")
    print("Token Decoding  : Passed")
    print()
    print("JWT test passed.")


if __name__ == "__main__":
    main()